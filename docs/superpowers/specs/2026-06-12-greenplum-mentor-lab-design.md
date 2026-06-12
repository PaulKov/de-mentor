# Greenplum Mentor Lab Design

## Цель

Собрать первый самостоятельный модуль для менторинга дата инженера: 60-минутный урок по Greenplum, практику с SQL, локальный Docker-стенд и CLI, который одинаково понятен ментору и ученику на macOS и Windows.

## Пользовательский Сценарий

Ментор открывает `docs/lessons/01-greenplum/README.md`, ведет урок по таймингу, дает ученику workbook и запускает лабораторный стенд через `python3 mentor-lab.py up greenplum`.

Ученик ставит Docker Desktop, запускает `python3 mentor-lab.py up greenplum` на macOS или `py mentor-lab.py up greenplum` на Windows, подключается через CLI и выполняет SQL-задания без локальной установки `psql`.

## Архитектура

Документация, SQL-лабораторная и CLI разделены. CLI содержит небольшую доменную модель `LabDefinition`, registry стендов и `DockerComposeRunner`, который строит команды Docker Compose и может работать в dry-run режиме.

Такой дизайн сохраняет KISS для первого урока и оставляет расширение под ClickHouse, Postgres, HDFS, Spark on YARN и Spark on Kubernetes через новые lab definitions.

## Greenplum Стенд

Greenplum запускается в Docker Compose на базе образа `woblerr/greenplum:7.1.0`. Init scripts монтируются в `/docker-entrypoint-initdb.d`, создают учебную схему, измерения, факт с плохим распределением и факт с исправленным распределением.

## Тестирование

Автотесты покрывают:

- registry готовых и планируемых стендов;
- генерацию Docker Compose команд;
- CLI list/info/up dry-run и понятную ошибку для неизвестного стенда.

## Границы

В первой версии не разворачиваются ClickHouse, Hadoop и Spark. Они зафиксированы в registry как planned, чтобы интерфейс не менялся при расширении платформы.
