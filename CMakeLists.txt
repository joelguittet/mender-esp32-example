# @file      CMakeLists.txt
# @brief     mender-esp32-example CMakeLists file
#
# Copyright joelguittet and mender-mcu-client contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

cmake_minimum_required(VERSION 3.5)

# Read VERSION
file(STRINGS ${CMAKE_SOURCE_DIR}/VERSION.txt PROJECT_VER LIMIT_COUNT 1)
set_property(DIRECTORY . APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS ${CMAKE_SOURCE_DIR}/VERSION.txt)

# Extra components
set(EXTRA_COMPONENT_DIRS $ENV{IDF_PATH}/examples/common_components/protocol_examples_common)

# Declare project
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(mender-esp32-example)
