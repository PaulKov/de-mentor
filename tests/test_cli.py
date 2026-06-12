from contextlib import redirect_stdout
from io import StringIO

from mentor_lab.cli import main


def invoke(args):
    stdout = StringIO()
    with redirect_stdout(stdout):
        exit_code = main(args)
    return exit_code, stdout.getvalue()


def test_list_command_shows_ready_and_planned_labs():
    exit_code, output = invoke(["list"])

    assert exit_code == 0
    assert "greenplum" in output
    assert "ready" in output
    assert "spark-k8s" in output
    assert "planned" in output


def test_up_dry_run_prints_cross_platform_docker_compose_command():
    exit_code, output = invoke(["up", "greenplum", "--dry-run"])

    assert exit_code == 0
    assert "docker compose -f" in output
    assert "labs/greenplum/docker-compose.yml up -d" in output


def test_info_command_gives_student_friendly_greenplum_entrypoint():
    exit_code, output = invoke(["info", "greenplum"])

    assert exit_code == 0
    assert "python3 mentor-lab.py up greenplum" in output
    assert "py mentor-lab.py up greenplum" in output
    assert "macOS" in output
    assert "Windows" in output


def test_unknown_lab_returns_clear_error():
    exit_code, output = invoke(["up", "oracle", "--dry-run"])

    assert exit_code == 1
    assert "Unknown lab 'oracle'" in output
    assert "greenplum" in output

