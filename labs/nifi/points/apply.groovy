import groovy.json.JsonSlurper
import org.apache.nifi.processor.io.InputStreamCallback

def ff = session.get()
if (ff == null) return
def event
session.read(ff, { input -> event = new JsonSlurper().parse(input) } as InputStreamCallback)

String decision
CTL.points.getConnection().withCloseable { db ->
    db.setAutoCommit(false)
    try {
        db.prepareStatement('select points_lab.credit(?::uuid, ?, ?, ?, ?, ?, ?::uuid)').withCloseable { stmt ->
            stmt.setString(1, event.event_id)
            stmt.setString(2, event.account_id)
            stmt.setInt(3, event.points)
            stmt.setString(4, ff.getAttribute('kafka.topic'))
            stmt.setInt(5, ff.getAttribute('kafka.partition').toInteger())
            stmt.setLong(6, ff.getAttribute('kafka.offset').toLong())
            stmt.setString(7, ff.getAttribute('uuid'))
            stmt.executeQuery().withCloseable { result ->
                result.next()
                decision = result.getString(1)
            }
        }
        db.commit()
    } catch (Exception error) {
        db.rollback()
        throw error
    }

    if (decision == 'applied' && event.pause_after_commit == true) {
        // This is a separate transaction. The student can observe the pause from pg_stat_activity.
        db.setAutoCommit(true)
        db.prepareStatement("select set_config('application_name', ?, false)").withCloseable { tag ->
            tag.setString(1, "points-drill:" + event.event_id)
            tag.execute()
        }
        try {
            db.createStatement().withCloseable { it.execute('select pg_sleep(180) /* points_lab_gate */') }
        } finally {
            db.createStatement().withCloseable { it.execute('reset application_name') }
        }
    }
}
ff = session.putAttribute(ff, 'points.decision', decision)
session.transfer(ff, decision == 'conflict' ? REL_FAILURE : REL_SUCCESS)
