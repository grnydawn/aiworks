# Operational TRITON

## Document Control

**Current Version:** 0.1  
**Last Updated:** 12/2/2025  
**Owner:** Youngsung Kim

### Change Log
- **0.1 (2025-12-02)** — Working draft  

---

## 1. Project Overview

### 1.1 Project Title
Operational TRITON

### 1.2 Project Summary
This project aims to support the USAF in developing a scalable global flood inundation forecasting framework. It involves enhancing the existing end-to-end TRITON inundation forecasting workflow prototype at Osan AFB, improving automation and robustness, and scaling it to additional sites.

### 1.3 Background / Problem Statement
- **Problem:** Need for a robust, scalable global flood inundation forecasting framework for USAF operations.
- **Context:** Building upon the NASA-ERDC-NGA-ORNL collaboration which explored GHI–LIS data subscription on HPC11 for TRITON testing. Previous work includes sharing datasets with ERDC for AutoRoute model development and ongoing coordination.

### 1.4 Vision Statement
To integrate AutoRoute and TRITON into a unified forecasting framework, transitioning TRITON to operations on AFW HPC11, and leveraging it for high-resolution inundation modeling for critical areas of interest.

---

## 2. Objectives & Success Criteria

### 2.1 Project Objectives
- Support USAF in developing a scalable global flood inundation forecasting framework.
- Enhance the existing TRITON prototype at Osan AFB (automation & robustness).
- Scale and expand the prototype to two additional sites (e.g., Offutt AFB, McConnell AFB).
- Evaluate GHI–LIS runoff and streamflow products by validating impacts on simulated inundation extents.
- Collaborate with ERDC to integrate AutoRoute and TRITON.
- Assist USAF personnel in transitioning TRITON to operations on AFW HPC11.

### 2.2 Success Criteria
- Successful deployment and operation of the enhanced TRITON workflow at Osan AFB.
- Successful expansion to two additional sites.
- Validation of GHI-LIS products against observations and benchmarks.
- Operational transition of TRITON on AFW HPC11.
- Functional "threshold-based trigger" capability.

---

## 3. Project Scope

### 3.1 In-Scope
- **Sites:** Osan AFB, Offutt AFB, McConnell AFB.
- **Integration:** AutoRoute and TRITON unified framework.
- **Validation:** GHI–LIS runoff and streamflow products.
- **Operations:** Transition to AFW HPC11.
- **Workflow:** Automation, robustness, and remote monitoring.

### 3.2 Out-of-Scope
- [Suggest: Development of new hydrological models from scratch (using existing GHI-LIS/AutoRoute)]
- [Suggest: Hardware procurement (using existing HPC11/private HPC)]

### 3.3 Assumptions
- Access to USAF data feeds and missing data (coordination required).
- Availability of HPC11 and private HPC resources.
- Continued collaboration with NASA, ERDC, NGA, and ORNL.
- Data inputs available every 3 hours.

### 3.4 Constraints
- **System:** Must run on a private HPC system.
- **Reliability:** High reliability required, potentially requiring dual execution for redundancy.
- **Monitoring:** Operation must be remotely monitored.
- **Data:** Data-availability check must run frequently (more than every 3 hours).

---

## 4. Deliverables

### 4.1 Main Deliverables
- Enhanced TRITON workflow code and scripts.
- Configuration for Osan, Offutt, and McConnell AFBs.
- Validation report for GHI-LIS products.
- Operational documentation for AFW HPC11 transition.

### 4.2 Interim Deliverables / Checkpoints
- Prototype enhancement at Osan AFB.
- Deployment at first additional site.
- Deployment at second additional site.
- Integration test of AutoRoute and TRITON.

---

## 5. Requirements

### 5.1 Functional Requirements
- **Workflow Structure:** Three steps: Data Preparation → Simulation → Reporting.
- **Automation:** Each step launches the next upon completion.
- **Data Check:** First step checks for data availability before starting; checks more frequently than the 3-hour data update cycle.
- **Trigger:** Threshold-based trigger for high-resolution modeling.

### 5.2 Non-Functional Requirements
- **Reliability:** High reliability, dual execution for redundancy.
- **Scalability:** Support for multiple global sites.
- **Latency:** Support Near Real-Time (NRT) operations.

### 5.3 Data & Resource Requirements
- **Inputs:** GHI-LIS data, DEM, Manning’s n, stream network, streamflow, baseflow.
- **Source:** /lustre/cyclone/nwp500/proj-shared/g7h/e2e_prototype/ (and rsync script).
- **Compute:** AFW HPC11.

---

## 6. High-Level Architecture

### 6.1 Architecture Summary
The system follows a linear pipeline: Data Preparation → Simulation → Reporting. It is event-driven, with data availability triggering the workflow. It is designed for HPC environments.

### 6.2 Technology Stack
- **HPC:** AFW HPC11
- **Models:** TRITON, AutoRoute, GHI-LIS.
- **Scripting:** Shell (rsync), likely Python/Bash for workflow orchestration.

---

## 7. Personal Workflow Plan

### 7.1 Development Workflow
- [Suggest: Git-based version control]
- [Suggest: Regular syncs with USAF/ERDC]

### 7.2 Testing Strategy
- Validation against observations and benchmark datasets.
- Intercomparison between TRITON and AutoRoute.

### 7.3 Development Process
1. Analyze existing prototype (/lustre/cyclone/nwp500/proj-shared/g7h/e2e_prototype/).
2. Enhance automation and robustness.
3. Deploy to new sites.
4. Validate and Integrate.
5. Transition to Operations.

---

## 8. Timeline & Milestones

### 8.1 Timeline
[Suggest: Define timeline based on funding/project duration]

### 8.2 Milestones
- **M1:** Osan AFB prototype enhanced.
- **M2:** AutoRoute integration design complete.
- **M3:** Expansion to Offutt and McConnell AFBs.
- **M4:** Operational transition to HPC11.

### 8.3 Completion Criteria per Milestone
- Successful execution of workflow without manual intervention.
- Validation metrics meeting defined thresholds.

---

## 9. Risks & Mitigation

### 9.1 Primary Risks
- Data feed interruptions or format changes.
- Access issues with USAF HPC systems.
- Integration challenges between different models.

### 9.2 Mitigation Strategies
- Dual execution for redundancy.
- Close coordination with USAF and ERDC points of contact.

---

## 10. Acceptance Criteria
- Fully automated, robust forecasting workflow running on AFW HPC11.
- Successful validation of inundation extents.
- USAF personnel trained/capable of operating the system.

---

## 11. Version Control & Documentation

### 11.1 Repo Location
[Insert Repo URL]

### 11.2 Documentation Plan
- README for workflow setup.
- Operational manual for monitoring and troubleshooting.

---

## 12. Stakeholders & Glossary

### 12.1 Organizations
- **USAF:** Project owner.
- **NASA:** Spaceborne + global hydrology.
- **ERDC:** Flood engineering for operations.
- **NGA:** Geospatial/intel + terrain + population.
- **ORNL:** Exascale modeling + impact analytics + data delivery.

### 12.2 Glossary
- **GFMS:** Global Flood Monitoring System
- **GHI:** Global Hydrology Infrastructure
- **LIS:** Land Information System
- **TRITON:** Two-dimensional Runoff Inundation Toolkit for Operational Needs
- **NRT:** Near Real-Time (3–6 h latency)
- **Medium Range:** Forecasts extending about 3–10 days ahead
- **AutoRoute:** Rapid flood inundation model
