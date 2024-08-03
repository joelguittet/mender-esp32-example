# @file      CMakeLists.txt
# @brief     msgpack-c component CMakeLists file
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

# List of sources
list(APPEND srcs
    "${CMAKE_CURRENT_LIST_DIR}/msgpack-c/src/objectc.c"
    "${CMAKE_CURRENT_LIST_DIR}/msgpack-c/src/unpack.c"
    "${CMAKE_CURRENT_LIST_DIR}/msgpack-c/src/version.c"
    "${CMAKE_CURRENT_LIST_DIR}/msgpack-c/src/vrefbuffer.c"
    "${CMAKE_CURRENT_LIST_DIR}/msgpack-c/src/zone.c"
)

# List of includes
list(APPEND includes
    "${CMAKE_CURRENT_LIST_DIR}/include"
    "${CMAKE_CURRENT_LIST_DIR}/include/msgpack"
    "${CMAKE_CURRENT_LIST_DIR}/msgpack-c/include"
)

# Register msgpack-c component
idf_component_register(
    SRCS ${srcs}
    INCLUDE_DIRS ${includes}
)
