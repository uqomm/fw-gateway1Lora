# Changelog# Changelog



All notable changes to the LoRa Gateway Firmware project will be documented in this file.All notable changes to the LoRa Gateway Firmware project will be documented in this file.



The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),

and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).



## [2.6.0] - 2025-10-16 - Logger System Implementation## [2.6.0] - 2025-10-16 - Logger System Implementation



**JIRA Reference**: FWL-EPIC-001 - LoRa Gateway Logger System Implementation**JIRA Reference**: FWL-EPIC-001 - LoRa Gateway Logger System Implementation  

**Base Version**: v2.5.1 (2025-10-09)**Base Version**: v2.5.1 (2025-10-09)  

**Purpose**: Complete embedded logger system with GUI tools and enhanced monitoring capabilities**Purpose**: Complete embedded logger system with GUI tools and enhanced monitoring capabilities



### Added - Logger System Implementation### Added - Logger System Implementation

- **Embedded Logger System**: Comprehensive logging infrastructure for STM32F103- **Embedded Logger System**: Comprehensive logging infrastructure for STM32F103

  - `Logger.hpp/Logger.cpp` with singleton pattern implementation  - `Logger.hpp/Logger.cpp` with singleton pattern implementation

  - Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)  - Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)

  - RS485 output via UART3 with automatic DE/RE control  - RS485 output via UART3 with automatic DE/RE control

  - Message formatting with timestamps and source identification  - Message formatting with timestamps and source identification

  - Hardware abstraction for different logging targets  - Hardware abstraction for different logging targets



- **Logger Integration**: Comprehensive firmware integration- **GUI Configuration Application**: Complete Python tkinter interface

  - Logger initialization in main.cpp startup sequence  - `lora_gui_config.py` with 4-tab interface (Connection, Parameters, Advanced, Log)

  - Heartbeat logging with system status monitoring  - `radio_command_codes.py` for command definitions

  - UART/LoRa communication logging for debugging  - Serial communication with real-time monitoring

  - Error handling and monitoring integration  - Parameter configuration and validation

  - Complete logging pipeline testing and validation  - Log viewing and export functionality



### Added - Project Management- **Enhanced LoRa Monitoring**: Parameter logging in heartbeat

- **Repository Structure Cleanup**: Complete reorganization (2025-10-16)  - RX/TX frequency logging in heartbeat messages

  - Moved STM32 project files to dedicated `project/` folder  - Spread factor, coding rate, bandwidth parameter tracking

  - Organized documentation in `docs/` with firmware/tools subfolders  - Real-time transmission parameter monitoring

  - Removed obsolete JIRA scripts and batch files  - Integration with Logger system for comprehensive debugging

  - Updated build/flash scripts for new project structure

  - Replaced PowerShell scripts with cross-platform Python equivalents### Changed - System Architecture

- **UART Migration**: Improved communication architecture

### Technical Details  - Migrated from UART1 to UART2 for LoRa data communication

- **Development Time**: 10.5 hours total (2025-10-16, 09:00-17:00 + repository cleanup)  - Updated all UART configuration and initialization code

- **Efficiency**: 100% (perfect time estimation accuracy)  - Enhanced communication reliability and timing

- **Memory Impact**: +3KB flash for logger system, +1.5KB for GUI support  - Maintained backward compatibility where needed

- **Performance**: Real-time logging with <1ms overhead per message

- **Logger Integration**: Comprehensive firmware integration

### Task Breakdown  - Logger initialization in main.cpp startup sequence

1. **FWL-001**: Implement Embedded Logger System (2.5h) ✅  - Heartbeat logging with system status monitoring

2. **FWL-002**: UART1 to UART2 Migration (1.0h) ✅  - UART/LoRa communication logging for debugging

3. **FWL-003**: Logger System Integration (1.5h) ✅  - Error handling and monitoring integration

4. **FWL-004**: LoRa Parameters in Heartbeat Logging (1.0h) ✅  - Complete logging pipeline testing and validation

5. **FWL-005**: GUI Configuration Application (1.5h) ✅

6. **FWL-006**: Repository Migration and Organization (0.5h) ✅### Added - Project Management

7. **FWL-007**: Repository Migration and Organization (duplicate - merged) ✅- **Repository Migration**: Professional project organization

8. **FWL-008**: Repository Structure Cleanup and Organization (2.5h) ✅  - Transferred repository to uqomm/fw-gateway1Lora organization

  - Updated documentation and README files

### Related Issues  - Configured proper access permissions and workflows

- Epic: FWL-EPIC-001 (Logger System Implementation)  - Updated build and deployment scripts for new structure

- Base version: v2.5.1 (Project Management & Refinements)- **Repository Structure Cleanup**: Complete reorganization (2025-10-16)

- Branch: main (production ready)  - Moved STM32 project files to dedicated `project/` folder

  - Organized documentation in `docs/` with firmware/tools subfolders

## [2.5.1] - 2025-10-09 - FG-4 Refinements  - Removed obsolete JIRA scripts and batch files

  - Updated build/flash scripts for new project structure

**JIRA Reference**: FG-4 - v2.5.0 Refinements & Project Management  - Replaced PowerShell scripts with cross-platform Python equivalents

**Base Version**: v2.5.0 (2025-10-08)

**Purpose**: Firmware cleanup, conditional compilation improvements, and project management automation### Technical Details
- **Development Time**: 10.5 hours total (2025-10-16, 09:00-17:00 + repository cleanup)
- **Efficiency**: 100% (perfect time estimation accuracy)
- **Memory Impact**: +3KB flash for logger system, +1.5KB for GUI support
- **Performance**: Real-time logging with <1ms overhead per message

### Task Breakdown
1. **FWL-001**: Implement Embedded Logger System (2.5h) ✅
2. **FWL-002**: UART1 to UART2 Migration (1.0h) ✅  
3. **FWL-003**: Logger System Integration (1.5h) ✅
4. **FWL-004**: LoRa Parameters in Heartbeat Logging (1.0h) ✅
5. **FWL-005**: GUI Configuration Application (1.5h) ✅
6. **FWL-006**: Repository Migration and Organization (0.5h) ✅
7. **FWL-007**: Repository Migration and Organization (duplicate - merged) ✅
8. **FWL-008**: Repository Structure Cleanup and Organization (2.5h) ✅

### Related Issues
- Epic: FWL-EPIC-001 (Logger System Implementation)
- Base version: v2.5.1 (Project Management & Refinements)
- Branch: main (production ready)

## [2.5.1] - 2025-10-09 - FG-4 Refinements

**JIRA Reference**: FG-4 - v2.5.0 Refinements & Project Management  
**Base Version**: v2.5.0 (2025-10-08)  
**Purpose**: Firmware cleanup, conditional compilation improvements, and project management automation

### Added - Project Management Automation
- **JIRA Integration Scripts**: Comprehensive project management automation
  - `jira_manager.py` - Unified JIRA operations with parameter support
  - Automated daily worklog tracking and task status synchronization
  - Epic hierarchy creation and organization tools
  - CHANGELOG-driven JIRA updates and validation

- **Epic Hierarchy Organization**: Proper JIRA project structure
  - FG-1: Base Versions Epic (contains v2.4.0, v2.5.0 releases)
  - FG-2: FSK Server Development Epic (future v3.0.0+ development)
  - Task → Subtask relationships for detailed work breakdown
  - Status synchronization: All v2.4.0/v2.5.0 tasks marked DONE

### Changed - Firmware Refinements
- **Watchdog Control**: Conditional compilation for watchdog timer
  - `ENABLE_WATCHDOG` define (default: 0/disabled for development)
  - Conditional `MX_IWDG_Init()` call in main.cpp
  - Safe watchdog disable for debugging and testing phases

- **System Clock Optimization**: Performance improvements for STM32F103
  - CPU clock configuration optimized for stable operation
  - Peripheral timing adjustments for better performance
  - FLASH latency optimization for enhanced stability
  - All peripheral clocks properly scaled (APB1, APB2, AHB)

### Removed - Code Cleanup
- **Debug Utilities**: Removed diagnostic files for production readiness
  - Deleted development-only diagnostic code
  - Removed SysTick diagnostic utilities from main.cpp
  - Cleaned up HAL_Delay test routines
  - Eliminated debug printf redirections

### Technical Improvements
- **Conditional Compilation**: Better development vs production builds
  - Watchdog can be enabled/disabled without code changes
  - Diagnostic code removed from production builds
  - Cleaner main.cpp with focused initialization

### Project Management
- **JIRA Status Updates**: Complete project organization
  - FG-1 (Base Versions): Completed with released versions
  - FG-2 (FSK Development): Ready for future development
  - All subtasks properly linked and status-synchronized
  - Complete development activity tracking

### Related Issues
- Base version: v2.5.0 (ID-596)
- Task: FG-4 (v2.5.0 Refinements)
- Branch: feature/fsk-reader-becker-varis

## [2.5.0] - 2025-10-08 - ID-596

**JIRA Reference**: ID-596 - Remote Diagnostic Data Capture Implementation  
**Base Version**: v2.4.0 (ID-540)  
**Purpose**: Enable remote diagnostics capabilities for industrial monitoring systems

### Added - Remote Diagnostics
- **SysTick Diagnostic Tools**: Comprehensive debugging utilities for HAL_Delay and timing issues
  - `debug_utils.h/c` module with specialized diagnostic functions
  - `GetSysTickDiagnostic()` - Captures complete SysTick timer state
  - `PrintSysTickDiagnostic()` - Formatted diagnostic output for remote monitoring
  - `TestDelay()` - Real-time validation of HAL_Delay functionality
  - `GetSysTickStatus()` - Quick status check for timing subsystem
  - DBGMCU freeze configuration monitoring during debug sessions
  
- **UART Debug Interface**: Printf support for real-time diagnostic output
  - `__io_putchar()` override implementation for UART1
  - Remote diagnostic data transmission capability
  - Debug message streaming for field troubleshooting
  - Integration with existing UART infrastructure

### Changed - Operational Improvements
- **Gateway Operation Mode**: Updated from RX_MODE to TX_RX_MODE
  - Full-duplex communication for diagnostic data exchange
  - Bidirectional command and diagnostic data flow
  - Enhanced gateway responsiveness for remote monitoring
  
- **LoRa Reception Reliability**: Improved packet reception timeout handling
  - RX timeout increased from 0ms to 2000ms
  - Better packet capture in noisy industrial environments
  - Reduced packet loss during diagnostic data transmission
  - Improved reliability for time-critical diagnostic commands

### Fixed - Development Environment
- **STM32CubeIDE Configuration**: Synchronized compiler settings
  - Updated environment configurations for STM32F103
  - Resolved build inconsistencies across development environments
  - Improved cross-platform compatibility

### Technical Details
- **Diagnostic System Architecture**:
  - Non-intrusive monitoring of SysTick subsystem
  - Real-time register capture without affecting system operation
  - Formatted output compatible with remote diagnostic protocols
  - Integration with HAL timing infrastructure

- **Remote Monitoring Capabilities**:
  - System clock frequency monitoring (SystemCoreClock)
  - HAL tick frequency and counter tracking
  - SysTick interrupt and enable status monitoring
  - Clock source configuration validation
  - DBGMCU peripheral freeze status reporting

### Performance Impact
- **Memory Footprint**: +2KB flash for diagnostic utilities
- **Runtime Overhead**: <0.1% CPU when not actively debugging
- **UART Bandwidth**: ~1200 bytes/s for full diagnostic output
- **Latency**: <5ms for diagnostic command response

### Related Issues
- Base version: ID-540 (FW-Gateway v2.4.0)
- Task: ID-596 (Remote Diagnostic Implementation)
- Branch: feature/fsk-reader-becker-varis

## [2.4.0] - 2025-07-07 - Batch Parameter Optimization

**JIRA Reference**: FG-3 - Batch Parameter Configuration & Performance Optimization  
**Purpose**: Intelligent parameter batching and UART performance improvements

### Added - Batch Parameter Configuration
- **Intelligent Batching System**: Optimized LoRa parameter updates
  - Tracks reception of all 5 parameters (TX_FREQ, RX_FREQ, BANDWIDTH, SPREAD_FACTOR, CODING_RATE)
  - Single EEPROM write and modem configuration per batch instead of per parameter
  - 2-second timeout protection for incomplete batches
  - 80% reduction in EEPROM write cycles for extended lifespan

- **Enhanced UART Interrupt Management**: Automatic restart system
  - Ensures continuous reception readiness after each command cycle
  - Proper state cleanup between commands for reliability
  - Improved error recovery and system robustness

### Enhanced - Performance Optimization
- **UART Response Time Optimization**: Sub-5ms response times
  - Immediate responses after RAM updates (previously 50-100ms)
  - Deferred EEPROM writes and modem configuration
  - Non-blocking command processing pipeline

- **LoRa Parameter Query Performance**: 1000-5000x improvement
  - Direct cached value access instead of EEPROM reads (previously 5-25ms)
  - Eliminated redundant operations for faster queries
  - Maintained data integrity through initialization loading

- **Optimized Message Composition**: Stack-based frame building
  - Eliminates dynamic vector allocations in `composeAndSendMessage()`
  - 50-70% performance improvement for message transmission
  - Reduced memory fragmentation and deterministic timing

### Enhanced - Tag Simulation
- **Advanced Tag Simulation**: Python-compatible implementation
  - Multiple detection modes (One Detection 0x17, Multiple Detection 0x18)
  - Advanced distance calculation and positioning logic
  - Configurable simulation parameters and realistic data generation
  - Improved algorithms for industrial environment testing

### Optimized - System Efficiency
- **EEPROM Usage Efficiency**: Significant lifecycle improvement
  - Batch processing reduces 5 individual writes to 1 per configuration session
  - Smart change detection and deferred persistence
  - Extended EEPROM lifespan and improved system reliability

- **Memory Management**: Eliminated unnecessary allocations
  - Stack-based buffer usage for message composition
  - Reduced heap fragmentation in embedded environment
  - More predictable memory usage patterns for real-time operation

### Fixed - Reliability Improvements
- **UART Frame Assembly**: Improved byte-by-byte reception handling
- **LoRa Reception Blocking**: Proper timing control during UART processing
- **CRC Calculation**: Enhanced frame validation and error detection
- **Command Parser State**: Reliable reset and cleanup mechanisms

### Technical Improvements
- **Code Architecture**: Better separation of immediate responses and background operations
- **Error Handling**: Robust timeout mechanisms and graceful degradation
- **Compatibility**: Maintained backward compatibility with existing command protocols

### Performance Metrics
- **UART Response Time**: <5ms (improved from 50-100ms)
- **Query Response Time**: <1ms (improved from 5-25ms)  
- **EEPROM Write Reduction**: 80% fewer cycles
- **Memory Allocations**: Eliminated ~10 dynamic allocations per message
- **Overall System Efficiency**: Significant real-time responsiveness improvement

### Related Issues
- Base version: v2.3.0 (Enhanced LoRa Gateway functionality)
- Task: FG-3 (Batch Parameter Configuration)
- Branch: feature/parameter-optimization

## [2.3.0] - 2025-09-04 - Repository Structure & Gateway Improvements

### Changed - Repository Organization
- **Repository Structure Reorganization**: Complete restructuring for improved project management
  - Moved STM32 projects to dedicated structure for better organization
  - Organized single LoRa gateway (STM32F103) project structure
  - Moved build artifacts to organized directories
  - Updated VS Code tasks and build system for new paths

- **Gateway LoRa Operation Mode**: Enhanced reception capabilities
  - Updated default operation mode from TX_MODE to RX_MODE
  - Improved message reception and processing capabilities
  - Better gateway functionality for field deployment

### Added - Documentation & Build System
- **Comprehensive Project Documentation**: Clear project structure documentation
  - Detailed README for project structure and features
  - Build instructions and configuration details
  - Project-specific feature descriptions and usage guides

- **Enhanced Build System**: Improved multi-environment support
  - Updated build scripts for new directory structure
  - Added tasks for STM32F103 project
  - Better organization of debugging and flashing tools

### Fixed - Development Environment
- **HAL Driver Consistency**: Updated and normalized STM32 HAL drivers
  - Consistent file formatting across all driver files
  - Updated license files and driver versions
  - Improved compatibility with development environment

### Related Issues
- Improvement task: Repository organization and gateway enhancements
- Branch: main (structure reorganization)

## [2.2.0] - 2024-XX-XX - Enhanced LoRa Gateway

### Added
- Enhanced LoRa Gateway functionality with improved response handling
- New sniffer tag simulation features
- Performance optimization improvements

### Enhanced
- Response handling optimization for better real-time performance
- UART command processing improvements
- Gateway reliability enhancements

## [2.1.0] - 2024-XX-XX - Communication Improvements

### Added
- Enhanced LoRa Gateway functionality with improved response handling
- New sniffer tag simulation features
- Communication protocol improvements

### Enhanced
- Response handling optimization
- UART command processing improvements

## [2.0.0] - 2024-XX-XX - Major Architecture Update

### Added
- Major firmware rewrite with improved architecture
- Enhanced LoRa communication protocols
- Comprehensive simulation capabilities

### Changed
- Complete refactor of core communication systems
- Improved error handling and reliability

## [1.0.0] - 2024-XX-XX - Initial Release

### Added
- Initial release of LoRa Gateway Firmware
- Basic LoRa communication functionality
- UART command interface
- Essential gateway operations