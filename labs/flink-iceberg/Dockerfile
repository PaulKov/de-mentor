ARG FLINK_VERSION=2.2.1
ARG ICEBERG_VERSION=1.12.0
ARG HADOOP_VERSION=3.3.6
ARG AWS_SDK_VERSION=1.12.367

FROM maven:3.9.9-eclipse-temurin-17 AS connector-jars
ARG FLINK_VERSION=2.2.1
ARG ICEBERG_VERSION=1.12.0
ARG HADOOP_VERSION=3.3.6
ARG AWS_SDK_VERSION=1.12.367
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
      -Dartifact=org.apache.hive:hive-exec:3.1.3 \
      -DoutputDirectory=/jars \
    && mvn -B org.apache.maven.plugins:maven-dependency-plugin:3.7.1:copy \
      -Dartifact=org.apache.thrift:libfb303:0.9.3 \
      -DoutputDirectory=/jars \
    && mvn -B org.apache.maven.plugins:maven-dependency-plugin:3.7.1:copy \
      -Dartifact=commons-logging:commons-logging:1.2 \
      -DoutputDirectory=/jars \
    && mvn -B org.apache.maven.plugins:maven-dependency-plugin:3.7.1:copy \
      -Dartifact=org.apache.hadoop:hadoop-client-api:${HADOOP_VERSION} \
      -DoutputDirectory=/jars \
    && mvn -B org.apache.maven.plugins:maven-dependency-plugin:3.7.1:copy \
      -Dartifact=org.apache.hadoop:hadoop-client-runtime:${HADOOP_VERSION} \
      -DoutputDirectory=/jars \
    && mvn -B org.apache.maven.plugins:maven-dependency-plugin:3.7.1:copy \
      -Dartifact=org.apache.hadoop:hadoop-aws:${HADOOP_VERSION} \
      -DoutputDirectory=/jars \
    && mvn -B org.apache.maven.plugins:maven-dependency-plugin:3.7.1:copy \
      -Dartifact=com.amazonaws:aws-java-sdk-bundle:${AWS_SDK_VERSION} \
      -DoutputDirectory=/jars

FROM flink:${FLINK_VERSION}-java17
ARG ICEBERG_VERSION=1.12.0
ARG HADOOP_VERSION=3.3.6
ARG AWS_SDK_VERSION=1.12.367
ARG FLINK_VERSION=2.2.1
USER root
COPY labs/flink-iceberg/conf/core-site.xml /opt/flink/conf/core-site.xml
COPY --from=connector-jars /jars/iceberg-flink-runtime-2.2-${ICEBERG_VERSION}.jar /opt/flink/lib/
COPY --from=connector-jars /jars/iceberg-aws-bundle-${ICEBERG_VERSION}.jar /opt/flink/lib/
COPY --from=connector-jars /jars/flink-sql-connector-kafka-5.0.0-2.2.jar /opt/flink/lib/
COPY --from=connector-jars /jars/hive-exec-3.1.3.jar /opt/flink/lib/
COPY --from=connector-jars /jars/libfb303-0.9.3.jar /opt/flink/lib/
COPY --from=connector-jars /jars/commons-logging-1.2.jar /opt/flink/lib/
COPY --from=connector-jars /jars/hadoop-client-api-${HADOOP_VERSION}.jar /opt/flink/lib/
COPY --from=connector-jars /jars/hadoop-client-runtime-${HADOOP_VERSION}.jar /opt/flink/lib/
COPY --from=connector-jars /jars/hadoop-aws-${HADOOP_VERSION}.jar /opt/flink/lib/
COPY --from=connector-jars /jars/aws-java-sdk-bundle-${AWS_SDK_VERSION}.jar /opt/flink/lib/
RUN chown flink:flink \
      /opt/flink/conf/core-site.xml \
      /opt/flink/lib/iceberg-flink-runtime-2.2-${ICEBERG_VERSION}.jar \
      /opt/flink/lib/iceberg-aws-bundle-${ICEBERG_VERSION}.jar \
      /opt/flink/lib/flink-sql-connector-kafka-5.0.0-2.2.jar \
      /opt/flink/lib/hive-exec-3.1.3.jar \
      /opt/flink/lib/libfb303-0.9.3.jar \
      /opt/flink/lib/commons-logging-1.2.jar \
      /opt/flink/lib/hadoop-client-api-${HADOOP_VERSION}.jar \
      /opt/flink/lib/hadoop-client-runtime-${HADOOP_VERSION}.jar \
      /opt/flink/lib/hadoop-aws-${HADOOP_VERSION}.jar \
      /opt/flink/lib/aws-java-sdk-bundle-${AWS_SDK_VERSION}.jar
USER flink
