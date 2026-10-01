FROM osrf/ros:jazzy-desktop

ENV DEBIAN_FRONTEND=noninteractive
USER root

RUN apt-get update && apt-get install -y \
    python3-pip \
    ros-jazzy-rmw-cyclonedds-cpp \
    git \
    wget \
    nano \
    && rm -rf /var/lib/apt/lists/*

ENV PIP_BREAK_SYSTEM_PACKAGES=1
RUN pip3 install --default-timeout=1000 --no-cache-dir pyserial

WORKDIR /root/ros2_ws

RUN echo "source /opt/ros/jazzy/setup.bash" >> /root/.bashrc
RUN echo "export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp" >> /root/.bashrc
RUN echo "export CYCLONEDDS_URI=file:///root/ros2_ws/cyclonedds.xml" >> /root/.bashrc

ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
ENV CYCLONEDDS_URI=file:///root/ros2_ws/cyclonedds.xml


CMD ["/bin/sh", "-c", "sleep infinity"]