FROM apache/spark:4.2.0-python3

USER root

COPY labs/spark/jupyter/requirements.txt /tmp/de-mentor-jupyter-requirements.txt

RUN python3 -m pip install --no-cache-dir \
    --requirement /tmp/de-mentor-jupyter-requirements.txt \
    && rm /tmp/de-mentor-jupyter-requirements.txt

WORKDIR /workspace/labs/spark/notebooks

EXPOSE 4040 8888

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
