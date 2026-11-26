import groovy.json.JsonOutput
import groovy.json.JsonSlurper
import org.apache.nifi.processor.io.StreamCallback

def flowFile = session.get()
if (!flowFile) return

try {
    flowFile = session.write(flowFile, { input, output ->
        def value = new JsonSlurper().parse(input)
        if (!(value instanceof Map) || !(value.event_id instanceof String) || !value.event_id.trim()) {
            throw new IllegalArgumentException('event_id must be a non-empty string')
        }
        value.event_id = value.event_id.trim()
        output.write(JsonOutput.toJson(value).getBytes('UTF-8'))
    } as StreamCallback)
    session.transfer(flowFile, REL_SUCCESS)
} catch (Exception e) {
    log.warn('Fixture could not be normalized', e)
    flowFile = session.putAttribute(flowFile, 'lab.error', 'invalid_json_or_event_id')
    session.transfer(flowFile, REL_FAILURE)
}
