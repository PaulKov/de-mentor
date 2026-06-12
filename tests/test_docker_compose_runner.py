from pathlib import Path

from mentor_lab.docker_compose import DockerComposeRunner
from mentor_lab.registry import create_default_registry


def test_up_command_uses_lab_compose_file_and_detached_mode():
    lab = create_default_registry(Path("/workspace")).get("greenplum")
    runner = DockerComposeRunner(project_root=Path("/workspace"))

    command = runner.build_up_command(lab)

    assert command == [
        "docker",
        "compose",
        "-f",
        "/workspace/labs/greenplum/docker-compose.yml",
        "up",
        "-d",
    ]


def test_reset_command_removes_volumes_for_clean_student_retry():
    lab = create_default_registry(Path("/workspace")).get("greenplum")
    runner = DockerComposeRunner(project_root=Path("/workspace"))

    command = runner.build_reset_command(lab)

    assert command == [
        "docker",
        "compose",
        "-f",
        "/workspace/labs/greenplum/docker-compose.yml",
        "down",
        "--volumes",
        "--remove-orphans",
    ]


def test_psql_command_uses_container_client_for_windows_and_macos():
    lab = create_default_registry(Path("/workspace")).get("greenplum")
    runner = DockerComposeRunner(project_root=Path("/workspace"))

    command = runner.build_psql_command(lab)

    assert command == [
        "docker",
        "compose",
        "-f",
        "/workspace/labs/greenplum/docker-compose.yml",
        "exec",
        "-u",
        "gpadmin",
        "greenplum",
        "bash",
        "-lc",
        ". /usr/local/greenplum-db/greenplum_path.sh && psql -U gpadmin -d mentor",
    ]


def test_healthcheck_command_uses_greenplum_environment():
    lab = create_default_registry(Path("/workspace")).get("greenplum")
    runner = DockerComposeRunner(project_root=Path("/workspace"))

    command = runner.build_healthcheck_probe_command(lab)

    assert command == [
        "su",
        "-",
        "gpadmin",
        "-c",
        ". /usr/local/greenplum-db/greenplum_path.sh && psql -U gpadmin -d mentor -c 'SELECT 1'",
    ]
