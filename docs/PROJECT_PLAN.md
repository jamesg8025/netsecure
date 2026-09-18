**NETSECURE**

**Project Plan**

*Network Asset and Vulnerability Scanner*

&nbsp;

| Team | NetSecure |
| :---- | :---- |
| **Project Manager / Network Scanning** | Zach |
| **Backend Development** | Austin |
| **Database Development** | Matt |
| **Frontend Development** | Izaiah |
| **Integration / Testing / GitHub** | James |

Planning target: project complete and presentation-ready by November 20, 2026

&nbsp;

&nbsp;

# **Document Control**

| Version | Date | Prepared By | Status |
| :---- | :---- | :---- | :---- |
| 1.0 | September 15, 2026 | NetSecure Team | Initial Project Plan |

# **Table of Contents**

1\. Project Overview

2\. Statement of Work (SOW)

3\. Resource List

4\. Work Breakdown Structure and Estimates

5\. Project Schedule and Critical Path

6\. Risk Management Plan

7\. Project Monitoring and Change Control

8\. Completion Criteria

# **1\. Project Overview**

**Project Purpose.** NetSecure is a web-based network asset and vulnerability scanning application that will help authorized users identify devices, open ports, running services, and potential security concerns on a local network. The system will combine Nmap-based network scanning, Python application logic, a web application backend, SQLite data storage, and a browser-based dashboard.

**Project Scope.** The project includes local-network discovery, port and service identification, scan-target validation, storage of scan history, display of discovered devices, security warning messages, severity indicators, and a web dashboard. The system is intended for authorized local or lab networks and will not perform exploitation, password attacks, malware analysis, or intrusive penetration testing.

**Planning Assumption.** This plan uses November 20, 2026 as the internal completion target so the team has time for final class requirements, instructor feedback, and presentation preparation. The exact framework choice (Flask vs. Django and Bootstrap vs. Tailwind CSS) remains a team decision and is treated as an early design milestone rather than a fixed requirement.

# **2\. Statement of Work (SOW)**

The NetSecure team will design, implement, integrate, test, document, and present a functioning network asset and security-scanning application. Work will be divided by primary technical ownership, but all members are expected to participate in integration, testing, documentation, and the final presentation.

| ID | Work Product | Work Description | Primary Owner(s) | Deliverable |
| :---- | :---- | :---- | :---- | :---- |
| WP-01 | Project Management and Documentation | Maintain project plan, coordinate milestones, meeting notes, SRS updates, and instructor deliverables. | Zach (lead); all members contribute | Project plan, SRS, meeting records, status reports |
| WP-02 | Network Scanning Component | Configure Nmap, validate local scan targets, perform host discovery, port/service detection, and produce structured scan output for the application. | Zach | Scanner module, scan profiles, Nmap setup notes, scanner test results |
| WP-03 | Backend Application | Implement the Python web backend, request handling, scan initiation, business logic, error handling, and communication among scanner, database, and frontend. | Austin | Backend application, routes/API interfaces, scan control logic, error responses |
| WP-04 | Database and Scan History | Design and implement SQLite storage for scans, hosts, ports/services, warnings, timestamps, and historical retrieval. | Matt | Database schema, initialization code, data-access functions, scan-history queries |
| WP-05 | Frontend Dashboard | Create the web interface for login, scan initiation, device lists, scan summaries, warnings, severity indicators, and scan history. | Izaiah | Dashboard pages, styles, scan-status UI, device and finding views |
| WP-06 | Integration, Testing, and Repository Management | Maintain GitHub workflow, integrate component branches, manage shared interfaces, perform system testing, coordinate bug fixes, and help maintain a stable main branch. | James | Integrated builds, test records, issue tracking, release candidate |
| WP-07 | Security Analysis Rules | Define and implement basic rules that map selected detected services/ports to plain-language warnings and severity levels. | Austin (logic), Zach (network input), Izaiah (display), Matt (storage) | Security rule set, finding records, severity presentation |
| WP-08 | Controlled Test Environment | Create and maintain an Ubuntu/VirtualBox test environment with authorized target systems for repeatable scanning and demonstrations. | Zach (lead), James (integration/testing) | VM lab, test targets, network configuration notes |
| WP-09 | Final Validation and Presentation | Complete end-to-end testing, final documentation, demonstration script, presentation materials, and final project submission. | All members; Zach coordinates | Final build, user/setup documentation, final presentation and demo |

# **3\. Resource List**

The following personnel, software, hardware, and information resources are expected to be required. Items marked TBD are available conceptually but require a team decision before implementation begins.

| Type | Resource | Availability | Use |
| :---- | :---- | :---- | :---- |
| Personnel | Zach \- project coordination / Nmap | Available throughout semester; schedule subject to school/work commitments | Primary scanning owner and coordinator |
| Personnel | Austin \- backend | Available throughout semester; schedule subject to school/work commitments | Primary backend owner |
| Personnel | Matt \- database | Available throughout semester; schedule subject to school/work commitments | Primary database owner |
| Personnel | Izaiah \- frontend | Available throughout semester; schedule subject to school/work commitments | Primary frontend owner |
| Personnel | James \- integration/testing | Available throughout semester; schedule subject to school/work commitments | Primary integration and GitHub owner |
| Repository | GitHub repository: jamesg8025/netsecure | Available now | Shared source control, pull requests, issues, documentation |
| Development | VS Code \+ Git | Available/free | Standard development and version-control tools |
| Runtime | Python 3.x | Available/free | Application logic and scan processing |
| Scanner | Nmap | Available/free | Network discovery, port and service identification |
| Backend | Flask or Django | TBD by team; both available/free | Web application framework |
| Frontend | HTML/CSS/JavaScript | Available | Core browser interface |
| CSS Framework | Bootstrap or Tailwind CSS | TBD by team; both available/free | Interface styling |
| Database | SQLite | Available/free | Local database and scan history |
| Virtualization | Oracle VirtualBox | Available/free | Controlled VM-based test network |
| Operating System | Ubuntu Linux | Available/free | Primary backend/scanner test environment |
| Test Targets | Windows/Linux virtual machines | Available as VMs; created as needed | Authorized devices for repeatable scans |
| Hardware | Team member computers | Available | Development and local testing |
| Communication | Discord / class meetings | Available | Team coordination |
| Documentation | Official Nmap, Python, SQLite, framework, Git/GitHub, VirtualBox documentation | Available online | Technical reference material |
| Course Support | Instructor feedback and course requirements | Available during course | Approval, grading criteria, scope guidance |

# **4\. Work Breakdown Structure and Estimates**

Estimates are planning values in person-hours and may be adjusted as the team learns more. The intent is to spread work across the semester, not to require every task to consume the full estimate.

| WBS | Task | Description | Owner | Est. Hours | Planned Window |
| :---- | :---- | :---- | :---- | :---- | :---- |
| 1.0 | Planning and Requirements | Finalize project plan, SRS, roles, scope, technology decisions, GitHub workflow | All / Zach lead | 18 | Sep 9-Sep 18 |
| 1.1 | Technology Decision | Choose Flask vs. Django and Bootstrap vs. Tailwind; document decision | All / Austin \+ Izaiah | 4 | Sep 9-Sep 18 |
| 1.2 | Development Setup | Standardize Git, Python, repo, branches, local environments | James lead | 8 | Sep 9-Sep 18 |
| 2.0 | Architecture and Interfaces | Define module boundaries, scan-result format, database interfaces, page/route map | All / James lead | 16 | Sep 16-Sep 27 |
| 3.0 | Nmap Scanner | Configure Nmap, target validation, host discovery, service scans, structured output parsing | Zach | 26 | Sep 21-Oct 18 |
| 4.0 | Backend Core | Create web app structure, routes/API, scan control, validation, processing and error handling | Austin | 30 | Sep 21-Oct 25 |
| 5.0 | Database | Create schema, initialization, persistence, queries, scan history | Matt | 22 | Sep 21-Oct 18 |
| 6.0 | Frontend | Build dashboard, scan page, device views, warnings, history, scan status | Izaiah | 28 | Sep 21-Oct 25 |
| 7.0 | Security Findings | Implement rule set, warning text, severity mapping, storage/display integration | Austin \+ Zach \+ Matt \+ Izaiah | 18 | Oct 12-Nov 1 |
| 8.0 | Component Integration | Connect scanner \-\> backend \-\> database \-\> frontend; resolve interface issues | James lead / all | 24 | Oct 19-Nov 8 |
| 9.0 | Authentication and Access Controls | Implement basic login/access control and authorized scan restrictions | James \+ Austin | 12 | Oct 26-Nov 8 |
| 10.0 | System Testing | Functional, integration, failure-path, repeatability, usability and compatibility tests | James lead / all | 24 | Nov 2-Nov 15 |
| 11.0 | Bug Fixing and Hardening | Resolve critical defects, improve error handling, polish scan rules and UI | All | 18 | Nov 9-Nov 15 |
| 12.0 | Final Documentation and Demo | Setup guide, final report updates, screenshots, demo plan, presentation practice | All / Zach coordinate | 18 | Nov 9-Nov 15 |

**Estimated total effort:** approximately 266 person-hours across the full team, including planning, development, integration, testing, documentation, and presentation work. This averages roughly 5-6 person-hours per member per week over the remaining project period, though work will vary by phase and role.

# **5\. Project Schedule and Critical Path**

The schedule below uses an internal completion target of November 20, 2026\. Critical-path tasks are marked YES. Delays to these tasks are most likely to delay the final integrated build because later work directly depends on them.

| ID | Task | Start | Finish | Depends On | Critical Path? |
| :---- | :---- | :---- | :---- | :---- | :---- |
| S1 | Project plan, SRS alignment, team setup | Sep 9 | Sep 18 | None | No |
| S2 | Finalize framework choices and architecture/interfaces | Sep 16 | Sep 27 | S1 | **YES** |
| S3 | Nmap scanner core and structured results | Sep 21 | Oct 18 | S2 | **YES** |
| S4 | Backend core and scan control | Sep 21 | Oct 25 | S2 | **YES** |
| S5 | Database schema and persistence | Sep 21 | Oct 18 | S2 | **YES** |
| S6 | Frontend dashboard and core views | Sep 21 | Oct 25 | S2 | No \- parallel |
| S7 | Security finding rules and severity model | Oct 12 | Nov 1 | S3, S4, S5 | No \- can overlap |
| S8 | First end-to-end integration | Oct 19 | Nov 8 | S3, S4, S5, S6 | **YES** |
| S9 | Authentication / access restrictions | Oct 26 | Nov 8 | S4 | No |
| S10 | Full system and failure-path testing | Nov 2 | Nov 15 | S8 | **YES** |
| S11 | Critical bug fixing / stabilization | Nov 9 | Nov 18 | S10 | **YES** |
| S12 | Final documentation, demo, presentation readiness | Nov 9 | Nov 20 | S8; final sign-off after S11 | **YES** |

**Primary critical path:** Architecture/interfaces \-\> Nmap scanner \+ backend \+ database completion \-\> first end-to-end integration \-\> full system testing \-\> stabilization/critical bug fixes \-\> final demonstration readiness.

**Schedule strategy.** Frontend development, security-rule refinement, authentication, and documentation can overlap the main critical path. The team should integrate small pieces as they become available rather than waiting until all components are individually complete.

## **5.1 Major Milestones**

| Milestone | Description | Target |
| :---- | :---- | :---- |
| M1 | Team environment and technology choices finalized | Sep 18 |
| M2 | Architecture/interfaces agreed | Sep 27 |
| M3 | Scanner, backend, database, and frontend core components demonstrated separately | Oct 25 |
| M4 | First complete scan-to-dashboard workflow | Nov 8 |
| M5 | System testing complete; no unresolved critical defects | Nov 15 |
| M6 | Final stable build and presentation-ready demo | Nov 15 |

# **6\. Risk Management Plan**

Risks will be reviewed during team meetings. When a risk begins to occur, the assigned owner should raise it immediately so the team can use the planned response before it becomes a schedule or quality problem.

| ID | Risk | Prob. | Impact | Prevention / Mitigation | Contingency | Owner |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| R1 | Framework decision is delayed | Medium | Medium | Set a decision deadline early; compare only the needs of NetSecure, not every feature of each framework. | Use the framework with which the responsible developers can deliver the required SRS features most reliably. | Austin / Izaiah |
| R2 | Nmap behaves differently across systems or requires permissions | Medium | High | Develop and test scanner primarily in the agreed Ubuntu environment; document Nmap version and required privileges. | Run scans from the controlled Ubuntu VM and adjust scan profile to a supported, non-intrusive configuration. | Zach |
| R3 | Unsafe or unauthorized scan targets | Low | High | Validate targets; default to private/local ranges; use only authorized lab or local networks. | Reject the scan and display a validation/error message. | Zach / Austin |
| R4 | Components do not integrate because data formats differ | Medium | High | Define interfaces/JSON/schema before major coding; use sample data early. | Freeze a minimal shared interface, adapt components to it, and defer nonessential fields. | James |
| R5 | Git merge conflicts or unstable main branch | Medium | Medium | Use feature branches, pull requests, small commits, and regular pulls from main. | James coordinates conflict resolution and restores last stable version if needed. | James |
| R6 | Database schema changes break other components | Medium | Medium | Agree on core schema early and version schema changes through GitHub. | Use migration/update scripts or temporarily support old fields until integration is restored. | Matt / James |
| R7 | VMs consume too many local resources | Medium | Medium | Use lightweight/dynamically allocated VMs and run only necessary targets. | Reduce VM count/resources or substitute lighter Linux targets for nonessential systems. | Zach |
| R8 | Scan performance freezes or delays the dashboard | Medium | High | Separate scan execution from normal page rendering; show scan-in-progress state. | Use background/asynchronous scan execution or a queued job approach supported by the selected backend. | Austin / James |
| R9 | Team member absence or uneven workload | Medium | High | Document work, use shared repo/issues, avoid knowledge being held by one person only. | Reassign the smallest necessary tasks; owner provides notes/code handoff. | Zach / James |
| R10 | Scope creep adds features beyond SRS | Medium | High | Treat SRS as baseline; new features require team agreement and schedule impact review. | Move nonessential ideas to a stretch-goal list until core requirements are complete. | Zach |
| R11 | Security warning rules produce misleading results | Medium | Medium | Describe findings as conditions requiring review, not proof of compromise; test rules against known lab systems. | Lower severity or revise wording; disable any rule that cannot be explained reliably. | Austin / Zach |
| R12 | Demo fails due to network/VM/environment issue | Low | High | Practice the final demo repeatedly on the same controlled environment; keep known-good VM snapshots and sample results. | Restore known-good snapshot and use a previously captured scan result to demonstrate history/UI if live scanning fails. | James / Zach |

# **7\. Project Monitoring and Change Control**

·         The team will review progress at least once each week using GitHub activity, assigned tasks, meeting notes, and milestone status.

·         Each member will report completed work, current work, blockers, and the next planned task.

·         Changes that affect scope, shared interfaces, technology choices, or the critical path must be discussed with the team before implementation.

·         Critical defects and integration blockers take priority over new optional features.

·         The SRS remains the baseline for required functionality. Features not needed to satisfy the SRS are stretch goals until the core system is stable.

# **8\. Completion Criteria**

NetSecure will be considered ready for final submission and presentation when the team can demonstrate the following in the agreed test environment:

·         An authorized user can access the NetSecure application.

·         A scan target can be entered/selected and validated before scanning.

·         Nmap can discover authorized local/lab devices and identify relevant ports/services.

·         Scan results are processed and stored with host information and timestamps.

·         The dashboard displays a readable scan summary and discovered devices.

·         Applicable detected services can generate plain-language warnings with severity indicators.

·         Previous scan results can be retrieved through scan history.

·         Failed scans or unavailable scanner conditions produce visible, logged errors.

·         The complete scanner \-\> backend \-\> database \-\> frontend workflow operates in the Ubuntu-based test environment.

·         No unresolved critical defects remain, and the team has a repeatable final demonstration procedure.

&nbsp;

## **Team Review / Sign-Off**

| Team Member | Signature | Date |
| :---- | :---- | :---- |
| Zach | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ | \_\_\_\_\_\_\_\_\_\_\_\_ |
| Austin | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ | \_\_\_\_\_\_\_\_\_\_\_\_ |
| Matt | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ | \_\_\_\_\_\_\_\_\_\_\_\_ |
| Izaiah | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ | \_\_\_\_\_\_\_\_\_\_\_\_ |
| James | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ | \_\_\_\_\_\_\_\_\_\_\_\_ |

&nbsp;

&nbsp;