# Find CUDA package
find_package(CUDAToolkit REQUIRED)

# Define the install directory for binaries
set(install_dir ${PROJECT_BINARY_DIR}/examples/bin)
set(cuSZp "cuSZp")
set(cuSZp_test_f32 "cuSZp_test_f32")
set(cuSZp_test_f64 "cuSZp_test_f64")
set(cuSZp_test_fixratio_f32 "cuSZp_test_fixratio_f32")
set(cuSZp_fixratio "cuSZp_fixratio")

# Include the main include directory
include_directories(${PROJECT_SOURCE_DIR}/include 
                    ${CUDAToolkit_INCLUDE_DIRS})

# Compile executable binaries
add_executable(${cuSZp} cuSZp.cpp)
add_executable(${cuSZp_test_f32} cuSZp_test_f32.cpp)
add_executable(${cuSZp_test_f64} cuSZp_test_f64.cpp)
add_executable(${cuSZp_test_fixratio_f32} cuSZp_test_fixratio_f32.cpp)
add_executable(${cuSZp_fixratio} cuSZp_fixratio.cpp)

# Link the existing cuSZp_static library
target_link_libraries(${cuSZp} PRIVATE cuSZp_static)
target_link_libraries(${cuSZp_test_f32} PRIVATE cuSZp_static)
target_link_libraries(${cuSZp_test_f64} PRIVATE cuSZp_static)
target_link_libraries(${cuSZp_test_fixratio_f32} PRIVATE cuSZp_static)
target_link_libraries(${cuSZp_fixratio} PRIVATE cuSZp_static)

# Set output paths for the compiled binary
set_target_properties(${cuSZp} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${install_dir})
set_target_properties(${cuSZp_test_f32} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${install_dir})
set_target_properties(${cuSZp_test_f64} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${install_dir})
set_target_properties(${cuSZp_test_fixratio_f32} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${install_dir})
set_target_properties(${cuSZp_fixratio} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${install_dir})

# Set installation paths for the compiled binary
install(TARGETS ${cuSZp} DESTINATION bin)
install(TARGETS ${cuSZp_test_f32} DESTINATION bin)
install(TARGETS ${cuSZp_test_f64} DESTINATION bin)
install(TARGETS ${cuSZp_test_fixratio_f32} DESTINATION bin)
install(TARGETS ${cuSZp_fixratio} DESTINATION bin)


# Test binary for cuSZp3 implementation phase
set(cuSZp_2D_float "cuSZp_2D_float")
set(cuSZp_3D_float "cuSZp_3D_float")
set(cuSZp_2D_double "cuSZp_2D_double")
set(cuSZp_3D_double "cuSZp_3D_double")
add_executable(${cuSZp_2D_float} cuSZp_2D_float.cpp)
add_executable(${cuSZp_3D_float} cuSZp_3D_float.cpp)
add_executable(${cuSZp_2D_double} cuSZp_2D_double.cpp)
add_executable(${cuSZp_3D_double} cuSZp_3D_double.cpp)
target_link_libraries(${cuSZp_2D_float} PRIVATE cuSZp_static)
target_link_libraries(${cuSZp_3D_float} PRIVATE cuSZp_static)
target_link_libraries(${cuSZp_2D_double} PRIVATE cuSZp_static)
target_link_libraries(${cuSZp_3D_double} PRIVATE cuSZp_static)
set_target_properties(${cuSZp_2D_float} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${install_dir})
set_target_properties(${cuSZp_3D_float} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${install_dir})
set_target_properties(${cuSZp_2D_double} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${install_dir})
set_target_properties(${cuSZp_3D_double} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${install_dir})
install(TARGETS ${cuSZp_2D_float} DESTINATION bin)
install(TARGETS ${cuSZp_3D_float} DESTINATION bin)
install(TARGETS ${cuSZp_2D_double} DESTINATION bin)
install(TARGETS ${cuSZp_3D_double} DESTINATION bin)

# New Test for 2D fixed ratio
set(test_fixed_ratio_2D "test_fixed_ratio_2D")
add_executable(${test_fixed_ratio_2D} test_fixed_ratio_2D.cpp)
target_link_libraries(${test_fixed_ratio_2D} PRIVATE cuSZp_static)
set_target_properties(${test_fixed_ratio_2D} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${install_dir})
install(TARGETS ${test_fixed_ratio_2D} DESTINATION bin)

# New Test for 1D fixed ratio
set(test_fixed_ratio_1D "test_fixed_ratio_1D")
add_executable(${test_fixed_ratio_1D} test_fixed_ratio_1D.cpp)
target_link_libraries(${test_fixed_ratio_1D} PRIVATE cuSZp_static)
set_target_properties(${test_fixed_ratio_1D} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${install_dir})
install(TARGETS ${test_fixed_ratio_1D} DESTINATION bin)

# New Test for 3D fixed ratio
set(test_fixed_ratio_3D "test_fixed_ratio_3D")
add_executable(${test_fixed_ratio_3D} test_fixed_ratio_3D.cpp)
target_link_libraries(${test_fixed_ratio_3D} PRIVATE cuSZp_static)
set_target_properties(${test_fixed_ratio_3D} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${install_dir})
install(TARGETS ${test_fixed_ratio_3D} DESTINATION bin)

# Multi-GPU Framework Test
set(test_multi_gpu_framework "test_multi_gpu_framework")
add_executable(${test_multi_gpu_framework} test_multi_gpu_framework.cpp)
target_link_libraries(${test_multi_gpu_framework} PRIVATE cuSZp_static)
set_target_properties(${test_multi_gpu_framework} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${install_dir})
install(TARGETS ${test_multi_gpu_framework} DESTINATION bin)

# Serial Chunked Test
set(test_serial_chunked "test_serial_chunked")
add_executable(${test_serial_chunked} test_serial_chunked.cpp)
target_link_libraries(${test_serial_chunked} PRIVATE cuSZp_static)
set_target_properties(${test_serial_chunked} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${install_dir})
install(TARGETS ${test_serial_chunked} DESTINATION bin)

# Find MPI
find_package(MPI REQUIRED)

# Multi-GPU HACC Test
set(test_multi_gpu_hacc "test_multi_gpu_hacc")
add_executable(${test_multi_gpu_hacc} test_multi_gpu_hacc.cpp)
target_link_libraries(${test_multi_gpu_hacc} PRIVATE cuSZp_static)
set_target_properties(${test_multi_gpu_hacc} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${install_dir})
install(TARGETS ${test_multi_gpu_hacc} DESTINATION bin)

# Multi-GPU Iso 3D Test (Single Node)
set(test_multi_gpu_iso "test_multi_gpu_iso")
add_executable(${test_multi_gpu_iso} test_multi_gpu_iso.cpp)
target_link_libraries(${test_multi_gpu_iso} PRIVATE cuSZp_static)
set_target_properties(${test_multi_gpu_iso} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${install_dir})
install(TARGETS ${test_multi_gpu_iso} DESTINATION bin)

# MPI Iso Test (Multi-Node)
set(test_mpi_iso "test_mpi_iso")
add_executable(${test_mpi_iso} test_mpi_iso.cpp)
target_link_libraries(${test_mpi_iso} PRIVATE cuSZp_static MPI::MPI_CXX)
set_target_properties(${test_mpi_iso} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${install_dir})
install(TARGETS ${test_mpi_iso} DESTINATION bin)

# CLI tool
set(cuszp_fixed_ratio_cli "cuszp_fixed_ratio_cli")
add_executable(${cuszp_fixed_ratio_cli} cuszp_fixed_ratio_cli.cpp)
target_link_libraries(${cuszp_fixed_ratio_cli} PRIVATE cuSZp_static)
set_target_properties(${cuszp_fixed_ratio_cli} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${install_dir})
install(TARGETS ${cuszp_fixed_ratio_cli} DESTINATION bin)

# 2D CLI tool
set(cuszp_fixed_ratio_cli_2d "cuszp_fixed_ratio_cli_2d")
add_executable(${cuszp_fixed_ratio_cli_2d} cuszp_fixed_ratio_cli-2d.cpp)
target_link_libraries(${cuszp_fixed_ratio_cli_2d} PRIVATE cuSZp_static)
set_target_properties(${cuszp_fixed_ratio_cli_2d} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${install_dir})
install(TARGETS ${cuszp_fixed_ratio_cli_2d} DESTINATION bin)

# 3D CLI tool
set(cuszp_fixed_ratio_cli_3d "cuszp_fixed_ratio_cli_3d")
add_executable(${cuszp_fixed_ratio_cli_3d} cuszp_fixed_ratio_cli-3d.cpp)
target_link_libraries(${cuszp_fixed_ratio_cli_3d} PRIVATE cuSZp_static)
set_target_properties(${cuszp_fixed_ratio_cli_3d} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${install_dir})
install(TARGETS ${cuszp_fixed_ratio_cli_3d} DESTINATION bin)
# Debug Sweep tool

# Debug Sweep tool
set(cuszp_debug_sweep_3d "cuszp_debug_sweep_3d")
add_executable(${cuszp_debug_sweep_3d} cuszp_debug_sweep_3d.cpp)
target_link_libraries(${cuszp_debug_sweep_3d} PRIVATE cuSZp_static)
set_target_properties(${cuszp_debug_sweep_3d} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${install_dir})
install(TARGETS ${cuszp_debug_sweep_3d} DESTINATION bin)

# ALL EB CHECK tool
set(cuSZp_all_eb_check "cuSZp_all_eb_check")
add_executable(${cuSZp_all_eb_check} cuSZp_all_eb_check.cpp)
target_link_libraries(${cuSZp_all_eb_check} PRIVATE cuSZp_static)
set_target_properties(${cuSZp_all_eb_check} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${install_dir})
install(TARGETS ${cuSZp_all_eb_check} DESTINATION bin)
