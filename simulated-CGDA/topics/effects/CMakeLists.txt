
IF (ENABLE_effects_py)

add_custom_target(effects_py ALL COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_SOURCE_DIR}/python/effects/effects.py ${CMAKE_BINARY_DIR}/bin)

INSTALL(FILES ${CMAKE_BINARY_DIR}/bin/effects.py DESTINATION ${CMAKE_INSTALL_PREFIX}/bin )

ENDIF (ENABLE_effects_py)

###execute_process(COMMAND ${CMAKE_COMMAND} -E cmake_echo_color --switch=$(COLOR) --cyan "..."
#execute_process(COMMAND ${CMAKE_COMMAND} -E echo "-- Copied python")
#execute_process(COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_SOURCE_DIR}/python/effects/effects.py ${CMAKE_BINARY_DIR}/bin)

#install(CODE "execute_process(COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_SOURCE_DIR}/python/effects/effects.py ${CMAKE_INSTALL_PREFIX}/bin)")
#add_custom_target(uninstall_effects_py COMMAND ${CMAKE_COMMAND} -E remove ${CMAKE_INSTALL_PREFIX}/bin/effects.py)

