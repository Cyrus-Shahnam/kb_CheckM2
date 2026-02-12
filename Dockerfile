FROM kbase/sdkpython:3.8.10
LABEL maintainer="ac.shahnam"

USER root

# ------------------------------------------------------------
# 1) micromamba bootstrap (same pattern you already use)
# ------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl bzip2 ca-certificates git && \
    rm -rf /var/lib/apt/lists/*

ENV MAMBA_ROOT_PREFIX=/opt/conda
ENV MAMBA_NO_BANNER=1
ENV MAMBA_DOCKERFILE_ACTIVATE=1

ENV MAMBA_ROOT_PREFIX=/opt/conda
ADD https://micro.mamba.pm/api/micromamba/linux-64/latest /tmp/micromamba.tar.bz2
RUN tar -xvjf /tmp/micromamba.tar.bz2 -C /usr/local/bin/ --strip-components=1 bin/micromamba && \
    chmod +x /usr/local/bin/micromamba && rm -f /tmp/micromamba.tar.bz2

RUN /opt/conda/envs/checkm2/bin/pip install jsonrpcbase jsonrpcserver kbase-common
    
# ------------------------------------------------------------
# 2) Create a CheckM2 environment
#    (env-checkm2.yml should live at module root)
# ------------------------------------------------------------
COPY env-checkm2.yml /tmp/env-checkm2.yml

# You can either:
#   a) specify checkm2 directly in env-checkm2.yml, OR
#   b) keep env-checkm2.yml minimal and install checkm2 here.
#
# This version assumes the YAML includes `checkm2` as a dependency.
RUN micromamba create -y -n checkm2 -f /tmp/env-checkm2.yml && \
    /opt/conda/envs/checkm2/bin/pip install --no-cache-dir \
        "numpy<1.24" \
        "pandas==1.5.3" \
        "tensorflow==2.13.*" \
        "keras==2.13.*" \
        "CheckM2==1.0.1" && \
    micromamba clean -a -y

RUN /opt/conda/envs/checkm2/bin/python -c "import os, checkm2; from importlib.metadata import version; p=os.path.join(os.path.dirname(checkm2.__file__),'models'); print('CheckM2', version('CheckM2')); print('models_dir', p); print('models_exists', os.path.isdir(p)); print('models_contents', os.listdir(p)[:200] if os.path.isdir(p) else 'N/A')"
RUN /opt/conda/envs/checkm2/bin/python -c "import tensorflow as tf, keras; print('tf', tf.__version__); print('keras', keras.__version__)"

# Make sure the env is on PATH at runtime
ENV PATH=/opt/conda/envs/checkm2/bin:$PATH

# ------------------------------------------------------------
# 3) (Optional but nice for dev) Download the CheckM2 database
# ------------------------------------------------------------
# WARNING: This is large. For dev images it’s fine; for production
# you may want ops to mount it on shared storage instead and just
# set CHECKM2DB in deploy.cfg.
RUN mkdir -p /kb/module/data/checkm2_db && \
    /opt/conda/envs/checkm2/bin/checkm2 database --download --path /kb/module/data/checkm2_db

# Set default DB path; impl will also accept database_path param
ENV CHECKM2DB=/kb/module/data/checkm2_db/CheckM2_database/CheckM2_database.dmnd


COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
