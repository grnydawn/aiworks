# Project Plan - Operational TRITON

## 1. Introduction
This project plan outlines the strategy for the Operational TRITON project, which aims to develop a scalable global flood inundation forecasting framework for the USAF. The project involves enhancing an existing prototype, scaling it to multiple sites, and transitioning it to operations on AFW HPC11.

## 2. Phase 1: Investigation & Analysis (Weeks 1-2)
**Goal:** deeply understand the existing codebase, data flows, and specific requirements for the operational system.

### 2.1 Codebase Analysis
We will investigate and analyze the following existing scripts in the `bin` folder to understand their current logic, dependencies, and limitations:
- **`bin/00_rsync.sh`**: Analyze the data ingestion process. Understand source paths, destination structures, and synchronization logic.
- **`bin/01_check_newday_convert.sh`**: Analyze how the system checks for new data and performs initial conversions.
- **`bin/A02_write_runoff_hyg_endtoend_LISarchive.py`**: Understand the core logic for processing runoff data and interfacing with the LIS archive.
- **`bin/lis_hpc11.py`**: Analyze the interface with the HPC11 environment and any specific configurations required.

### 2.2 Requirement Refinement
- Confirm specific data feed requirements and access protocols with USAF/ERDC.
- Define the exact "threshold-based trigger" logic.
- Map out the full dependency graph for the workflow.

## 3. Phase 2: Prototype Enhancement (Weeks 3-6)
**Goal:** Improve the automation, robustness, and reliability of the TRITON workflow at the initial site (Osan AFB).

### 3.1 Refactoring & Optimization
- Refactor the investigated scripts to improve error handling, logging, and maintainability.
- Modularize code to separate configuration from logic.

### 3.2 Componentization
- Split the refactored code into three components: Data Preparation, Simulation, and Reporting.

### 3.3 Automation Improvements
- Implement a robust data availability check that runs more frequently than the data update cycle.
- Automate the workflow steps: Data Preparation → Simulation → Reporting.
- Implement the threshold-based trigger mechanism.

### 3.4 Reliability & Redundancy
- Set up dual execution pipelines for redundancy.
- Implement remote monitoring capabilities to track system health and workflow status.

## 4. Phase 3: Expansion & Integration (Weeks 7-10)
**Goal:** Scale the system to additional sites and integrate the AutoRoute model.

### 4.1 Site Expansion
- Configure and deploy the enhanced workflow for **Offutt AFB**.
- Configure and deploy the enhanced workflow for **McConnell AFB**.

### 4.2 AutoRoute Integration
- Collaborate with ERDC to integrate the AutoRoute model into the unified framework.
- Ensure seamless data exchange between TRITON and AutoRoute components.

### 4.3 Validation
- Validate GHI-LIS runoff and streamflow products against observations and benchmark datasets.
- Compare simulated inundation extents with historical data.

## 5. Phase 4: Operational Transition (Weeks 11-12)
**Goal:** Finalize the system for operational use and hand it over to USAF.

### 5.1 Final Deployment
- Deploy the fully integrated and tested system to the **AFW HPC11** environment.
- Perform final acceptance testing.

### 5.2 Documentation & Training
- Create comprehensive operational documentation (User Manuals, Troubleshooting Guides).
- Conduct training sessions for USAF personnel.
- Formal project handover.
