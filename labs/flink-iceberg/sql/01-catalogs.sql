CREATE CATALOG lakekeeper WITH (
  'type' = 'iceberg',
  'catalog-type' = 'rest',
  'uri' = 'http://lakekeeper:8181/catalog',
  'warehouse' = 'flink-demo',
  'io-impl' = 'org.apache.iceberg.aws.s3.S3FileIO',
  's3.endpoint' = 'http://seaweedfs:8333',
  's3.path-style-access' = 'true',
  's3.access-key-id' = 'demouser',
  's3.secret-access-key' = 'demosecret123456',
  'client.region' = 'us-east-1'
);

CREATE CATALOG nessie WITH (
  'type' = 'iceberg',
  'catalog-type' = 'rest',
  'uri' = 'http://nessie:19120/iceberg'
);

SHOW CATALOGS;
