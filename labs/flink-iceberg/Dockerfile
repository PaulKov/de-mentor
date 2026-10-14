ARG FLINK_VERSION=2.2.1
ARG ICEBERG_VERSION=1.12.0
ARG HADOOP_VERSION=3.3.6

FROM maven:3.9.9-eclipse-temurin-17 AS connector-jars
ARG ICEBERG_VERSION=1.12.0
ARG HADOOP_VERSION=3.3.6
RUN mvn -B org.apache.maven.plugins:maven-dependency-plugin:3.7.1:copy \
      -Dartifact=org.apache.iceberg:iceberg-flink-runtime-2.2:${ICEBERG_VERSION} \
      -DoutputDirectory=/jars \
    && mvn -B org.apache.maven.plugins:maven-dependency-plugin:3.7.1:copy \
      -Dartifact=org.apache.iceberg:iceberg-aws-bundle:${ICEBERG_VERSION} \
      -DoutputDirectory=/jars \
    && mvn -B org.apache.maven.plugins:maven-dependency-plugin:3.7.1:copy \
      -Dartifact=org.apache.flink:flink-sql-connector-kafka:5.0.0-2.2 \
      -DoutputDirectory=/jars \
    && mvn -B org.apache.maven.plugins:maven-dependency-plugin:3.7.1:copy \
      -Dartifact=org.apache.hadoop:hadoop-client-api:${HADOOP_VERSION} \
      -DoutputDirectory=/jars \
    && mvn -B org.apache.maven.plugins:maven-dependency-plugin:3.7.1:copy \
      -Dartifact=org.apache.hadoop:hadoop-client-runtime:${HADOOP_VERSION} \
      -DoutputDirectory=/jars

FROM flink:${FLINK_VERSION}-java17
ARG ICEBERG_VERSION=1.12.0
ARG HADOOP_VERSION=3.3.6
USER root
COPY --from=connector-jars /jars/iceberg-flink-runtime-2.2-${ICEBERG_VERSION}.jar /opt/flink/lib/
COPY --from=connector-jars /jars/iceberg-aws-bundle-${ICEBERG_VERSION}.jar /opt/flink/lib/
COPY --from=connector-jars /jars/flink-sql-connector-kafka-5.0.0-2.2.jar /opt/flink/lib/
COPY --from=connector-jars /jars/hadoop-client-api-${HADOOP_VERSION}.jar /opt/flink/lib/
COPY --from=connector-jars /jars/hadoop-client-runtime-${HADOOP_VERSION}.jar /opt/flink/lib/
RUN chown flink:flink \
      /opt/flink/lib/iceberg-flink-runtime-2.2-${ICEBERG_VERSION}.jar \
      /opt/flink/lib/iceberg-aws-bundle-${ICEBERG_VERSION}.jar \
      /opt/flink/lib/flink-sql-connector-kafka-5.0.0-2.2.jar \
      /opt/flink/lib/hadoop-client-api-${HADOOP_VERSION}.jar \
      /opt/flink/lib/hadoop-client-runtime-${HADOOP_VERSION}.jar
USER flink
