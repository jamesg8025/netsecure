**NetSecure**

**Software Requirements Specification**

Senior Project Requirements Document

By: Zach, Matt, Austin, James, and Izaiah

| **Project**       | NetSecure                                 |
| ----------------- | ----------------------------------------- |
| **Document Type** | Software Requirements Specification (SRS) |
| **Version**       | Updated Draft                             |
| **Prepared For**  | Senior Projects                           |
| **Source**        | Updated Requirements Presentation         |

# Table of Contents

1\. Introduction

2\. Purpose

3\. Scope

4\. System Overview

5\. References

6\. Definitions

7\. Use Cases

8\. Functional Requirements

9\. Nonfunctional Requirements

10\. Requirements Traceability Matrix

11\. Open Decisions and Assumptions

# 1\. Introduction

NetSecure is a web-based network asset and vulnerability scanning application designed to help users identify devices, open ports, running services, and potential security concerns on an authorized local network. The system integrates network scanning, backend processing, database storage, and a web-based dashboard into a single application.

# 2\. Purpose

The purpose of this document is to define the requirements of the NetSecure project and provide the information necessary to guide its design, development, and testing. This document provides the information needed to understand the system's purpose, functionality, requirements, and expected behavior.

# 3\. Scope

This document provides a complete description of NetSecure's required functionality. Together, the use cases, functional requirements, and nonfunctional requirements define the system's expected behavior, capabilities, and constraints.

NetSecure will focus on authorized local and lab networks. It is intended to identify connected devices, ports, services, security findings, and scan history. NetSecure is not intended to perform exploitation, password attacks, malware analysis, or intrusive penetration testing.

# 4\. System Overview

NetSecure is a web-based application that scans authorized local networks to identify devices, open ports, running services, and potential security concerns. Users start scans through the dashboard. The backend processes and analyzes scan results, stores them in a database, and displays findings to the user.

**General system workflow:**

_User starts scan -> backend receives request -> Nmap scans the network -> Python processes results -> SQLite stores results -> security rules analyze results -> dashboard displays devices and findings._

**Major system components:**

- Nmap: Network discovery, port scanning, and network detection.
- Python: Application logic, scan processing, and security analysis.
- Web Application Backend: Handles communication between the user interface, scanning functionality, and stored data. The final framework may be Flask or Django.
- SQLite: Stores scan results, device information, and related findings.
- HTML/CSS/JavaScript: Provides the web-based user interface.
- GitHub: Provides version control and team collaboration.
- VirtualBox: Provides a controlled testing environment for system development.

# 5\. References

The following technologies and technical resources will be referenced throughout the development of NetSecure:

- Nmap - Nmap Reference Guide
- Python - Python 3 Documentation
- SQLite - SQLite Documentation
- Flask / Django - Web Application Framework Documentation
- Bootstrap / Tailwind CSS - Framework Documentation
- Git / GitHub - Git / GitHub Documentation
- Oracle VirtualBox - Oracle VirtualBox User Manual

# 6\. Definitions

| **Term**           | **Definition**                                                               |
| ------------------ | ---------------------------------------------------------------------------- |
| **Asset**          | A device connected to the network.                                           |
| **Host**           | A device identified during a network scan.                                   |
| **IP Address**     | A numerical address used to identify a device on a network.                  |
| **Port**           | A network communication endpoint.                                            |
| **Service**        | A network-accessible application running on a device.                        |
| **Network Scan**   | The process of examining a network to identify devices, ports, and services. |
| **Finding**        | A security-related observation generated from scan results.                  |
| **Vulnerability**  | A weakness that could potentially affect the security of a system.           |
| **Nmap**           | A network scanning tool used to discover devices, ports, and services.       |
| **Flask / Django** | Web application frameworks under consideration for the NetSecure backend.    |
| **SQLite**         | The database system used to store NetSecure scan information.                |

# 7\. Use Cases

The following use cases describe the primary interactions between authorized users and the NetSecure system.

- UC-01 Login
- UC-02 Start Network Scan
- UC-03 View Devices
- UC-04 View Security Threats
- UC-05 View Scan History

## UC-01 - Login

| **Summary**                | Allows users to securely access the NetSecure system using their login credentials.                                                                                                                                                                                 |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Rationale**              | Authentication ensures that only authorized users can access network scan results and system features.                                                                                                                                                              |
| **Users**                  | NetSecure user or administrator.                                                                                                                                                                                                                                    |
| **Preconditions**          | User has a NetSecure account, NetSecure is available, and the user has valid login credentials.                                                                                                                                                                     |
| **Basic Course of Events** | 1\. User navigates to the NetSecure login screen. <br>2\. User enters credentials. <br>3\. User selects the login button. <br>4\. NetSecure verifies the provided credentials. <br>5\. NetSecure authenticates the user. <br>6\. User is directed to the dashboard. |
| **Alternative Paths**      | If login information is incorrect, NetSecure prompts the user to try again. <br>If required fields are left blank, NetSecure prompts the user to fill in missing information.                                                                                       |
| **Postconditions**         | Authenticated user is granted access to the NetSecure dashboard.                                                                                                                                                                                                    |

## UC-02 - Start Network Scan

| **Summary**                | Allows an authorized user to start a network scan to discover devices.                                                                                                                                                                                                                       |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Rationale**              | Provides users with a way to identify devices and potential security concerns on a network.                                                                                                                                                                                                  |
| **Users**                  | Authorized users and administrators.                                                                                                                                                                                                                                                         |
| **Preconditions**          | User is logged in, scanning is available, and the system is connected to the target network.                                                                                                                                                                                                 |
| **Basic Course of Events** | 1\. User navigates to the scan page. <br>2\. User selects the scan button. <br>3\. NetSecure sends the scan request. <br>4\. The specified network is scanned. <br>5\. NetSecure receives and processes scan results. <br>6\. Results are stored. <br>7\. Results are displayed to the user. |
| **Alternative Paths**      | If no devices are discovered, NetSecure displays a message informing the user. <br>If the scan target is invalid or unauthorized, NetSecure displays a validation error. <br>If the scan fails, NetSecure logs the failure and displays a clear message.                                     |
| **Postconditions**         | Scan is completed, results are stored, and the user can view connected devices and security warnings.                                                                                                                                                                                        |

## UC-03 - View Devices

| **Summary**                | Allows an authorized user to view devices discovered during a network scan.                                                                                                                                                            |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Rationale**              | Provides the user with an organized view of devices connected to the scanned network and their basic information.                                                                                                                      |
| **Users**                  | Authorized users and administrators.                                                                                                                                                                                                   |
| **Preconditions**          | User is logged in, a network scan has been completed, and scan results are available.                                                                                                                                                  |
| **Basic Course of Events** | 1\. User navigates to the devices page. <br>2\. Results are retrieved. <br>3\. NetSecure displays the list of devices. <br>4\. User selects a device from the list. <br>5\. Available information on the selected device is displayed. |
| **Alternative Paths**      | If no devices are discovered, a message is displayed. <br>If no information for a selected device is available, an error message is displayed.                                                                                         |
| **Postconditions**         | User can view the discovered network devices and their available information.                                                                                                                                                          |

## UC-04 - View Security Threats

| **Summary**                | Allows an authorized user to view potential security threats that have been identified by a scan.                                                                                                                                                                             |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Rationale**              | Helps users identify devices at risk and services that may create risk on the network.                                                                                                                                                                                        |
| **Users**                  | Authorized users and administrators.                                                                                                                                                                                                                                          |
| **Preconditions**          | User is logged in, a network scan has been completed, and scan results are available.                                                                                                                                                                                         |
| **Basic Course of Events** | 1\. User navigates to security information. <br>2\. Results are retrieved. <br>3\. NetSecure identifies potential security threats. <br>4\. NetSecure displays information on identified security threats. <br>5\. Available information on the selected threat is displayed. |
| **Alternative Paths**      | If no threats are detected, NetSecure displays a message. <br>If results cannot be retrieved, NetSecure displays a message.                                                                                                                                                   |
| **Postconditions**         | User can view identified security threats.                                                                                                                                                                                                                                    |

## UC-05 - View Scan History

| **Summary**                | Allows an authorized user to view past scans performed in NetSecure.                                                                                                                                                                                                     |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Rationale**              | Provides users with a record of previous scans so they can review past results and track changes on the network.                                                                                                                                                         |
| **Users**                  | Authorized users and administrators.                                                                                                                                                                                                                                     |
| **Preconditions**          | User is logged in, previous network scans have been completed, and scan results are stored in the database.                                                                                                                                                              |
| **Basic Course of Events** | 1\. User navigates to the scan history page. <br>2\. Previous scan records are pulled from the database. <br>3\. NetSecure displays a list of previous scans. <br>4\. User selects a scan from the list. <br>5\. NetSecure displays the results from that previous scan. |
| **Alternative Paths**      | If no previous scans have been completed, NetSecure displays a message. <br>If the selected scan cannot be retrieved, NetSecure displays a message.                                                                                                                      |
| **Postconditions**         | User can view previous scan results and review historical information about the network.                                                                                                                                                                                 |

# 8\. Functional Requirements

The following functional requirements define the required behaviors and capabilities of NetSecure.

## FR-01

| **ID**           | FR-01                                                                                                                                                                                                                                                                                                |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Name**         | Use Nmap as the underlying scanning engine                                                                                                                                                                                                                                                           |
| **Summary**      | NetSecure will rely on Nmap to perform network discovery and port/service identification.                                                                                                                                                                                                            |
| **Rationale**    | Nmap is a standard network scanning tool, allowing the project team to focus on processing, storage, and user interface aspects of the system.                                                                                                                                                       |
| **Requirements** | The backend shall invoke Nmap through a controlled Python integration or library. <br>The backend shall support a basic scan profile for host discovery and related ports. <br>The system shall handle Nmap being unavailable or failing to execute with a clear error rather than failing silently. |
| **References**   | UC-02 Start Network Scan                                                                                                                                                                                                                                                                             |

## FR-02

| **ID**           | FR-02                                                                                                                                                                                                                                                                                   |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Name**         | Validate scan targets before launch                                                                                                                                                                                                                                                     |
| **Summary**      | Before a scan is executed, NetSecure checks that the requested target is well-formed and permitted instead of passing raw user input directly to Nmap.                                                                                                                                  |
| **Rationale**    | Unvalidated input passed to a shell-invoked service such as Nmap may create command-injection or misuse risks. Validation protects system integrity.                                                                                                                                    |
| **Requirements** | NetSecure shall verify that the target string matches expected IP address, subnet, or approved target formats before use. <br>The system shall reject input containing unexpected syntax. <br>The system shall return a clear validation error to the frontend if a target is rejected. |
| **References**   | UC-02 Start Network Scan                                                                                                                                                                                                                                                                |

## FR-03

| **ID**           | FR-03                                                                                                                                                                                                             |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Name**         | Store host IP, hostname, ports, and timestamps                                                                                                                                                                    |
| **Summary**      | Each scan is persisted to the database, capturing discovered hosts, IP addresses, hostnames when resolved, open ports/services, and the time of scan.                                                             |
| **Rationale**    | Persistence provides scan history, trend tracking, and the ability to compare network states over time.                                                                                                           |
| **Requirements** | The database schema shall include fields for host IP, hostname, open ports, associated services, and scan timestamp. <br>Each scan shall be associated with a unique scan ID to group discovered results per run. |
| **References**   | UC-02 Start Network Scan, UC-03 View Devices, UC-04 View Security Threats, UC-05 View Scan History                                                                                                                |

## FR-04

| **ID**           | FR-04                                                                                                                                                                                          |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Name**         | Display scan summaries on the dashboard                                                                                                                                                        |
| **Summary**      | The frontend presents a high-level, human-readable overview of scan results instead of raw Nmap output.                                                                                        |
| **Rationale**    | NetSecure is intended to be easier to understand than traditional command-line scanning tools. A summary view makes the output more accessible to users.                                       |
| **Requirements** | The dashboard shall display a list of discovered devices with key fields. <br>The dashboard shall visually differentiate devices or services with active warnings from those without warnings. |
| **References**   | UC-03 View Devices, UC-04 View Security Threats, UC-05 View Scan History                                                                                                                       |

## FR-05

| **ID**           | FR-05                                                                                                                                                                                                         |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Name**         | Generate warning messages explaining risky services                                                                                                                                                           |
| **Summary**      | When the security analysis logic flags a service, the system produces a plain-language explanation of the risk rather than only displaying a label.                                                           |
| **Rationale**    | Warnings are more useful when they explain why something may be risky and what the user should review.                                                                                                        |
| **Requirements** | The backend shall maintain a rule set mapping known risky ports or services to a human-readable explanation. <br>Each generated warning shall include the affected host, the port/service, and a description. |
| **References**   | UC-03 View Devices, UC-04 View Security Threats, UC-05 View Scan History                                                                                                                                      |

## FR-06

| **ID**           | FR-06                                                                                                                                                                                                                           |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Name**         | Assign severity or risk indicators to warnings                                                                                                                                                                                  |
| **Summary**      | Each warning is tagged with a severity level so users can quickly understand which issues deserve the most attention.                                                                                                           |
| **Rationale**    | Not all flagged services carry equal risk, so a severity indicator helps users triage and prioritize findings.                                                                                                                  |
| **Requirements** | The system shall define a severity scale applied consistently across all rules. <br>Each rule shall have a predefined severity assigned to it. <br>The severity level shall also be visually represented in the user interface. |
| **References**   | UC-03 View Devices, UC-04 View Security Threats, UC-05 View Scan History                                                                                                                                                        |

# 9\. Nonfunctional Requirements

The following nonfunctional requirements define quality attributes, constraints, and operating expectations for NetSecure.

## NFR-01

| **ID**           | NFR-01                                                                                                                                                                                                                                                            |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Name**         | Security - only approved targets may be scanned                                                                                                                                                                                                                   |
| **Summary**      | NetSecure shall allow users to view devices and scan results without enabling them to tamper with devices on the network.                                                                                                                                         |
| **Rationale**    | This allows users to safely and legally use NetSecure as a discovery and review tool rather than an intrusive attack tool.                                                                                                                                        |
| **Requirements** | The system shall restrict default scans to private or approved network ranges. <br>The system shall follow applicable legal and course policies for authorized network scanning. <br>The system shall not provide exploitation or device-tampering functionality. |
| **References**   | UC-03 View Devices, UC-04 View Security Threats                                                                                                                                                                                                                   |

## NFR-02

| **ID**           | NFR-02                                                                                                                                                                |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Name**         | Performance - scans should not freeze the dashboard                                                                                                                   |
| **Summary**      | When a scan occurs, the dashboard should remain usable and clearly indicate scan progress.                                                                            |
| **Rationale**    | If users experience freezing or unclear performance behavior, they may believe the software is faulty or avoid using it.                                              |
| **Requirements** | The backend should run scans without blocking normal dashboard responsiveness. <br>The frontend shall show a scan-in-progress indicator rather than appearing frozen. |
| **References**   | UC-02 Start Network Scan                                                                                                                                              |

## NFR-03

| **ID**           | NFR-03                                                                                                                                                                                                                       |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Name**         | Usability - results must be readable by users with basic networking knowledge                                                                                                                                                |
| **Summary**      | When scan data is gathered, it should be displayed in a clear and understandable format for users with basic networking knowledge.                                                                                           |
| **Rationale**    | If results are not readable, users will not understand the information NetSecure provides, which would reduce the value of the system.                                                                                       |
| **Requirements** | The frontend shall present scan results using an easy-to-read interface. <br>Labels, tables, findings, and warnings should use clear language. <br>Users should not need to read raw Nmap output to understand scan results. |
| **References**   | UC-03 View Devices, UC-04 View Security Threats, UC-05 View Scan History                                                                                                                                                     |

## NFR-04

| **ID**           | NFR-04                                                                                                                                                                                        |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Name**         | Reliability - failed scans must be logged                                                                                                                                                     |
| **Summary**      | If a scan fails, the failure must be logged so the user and team can understand what occurred.                                                                                                |
| **Rationale**    | If users are not informed of failed scans, they may incorrectly believe NetSecure is functioning or that no devices were found.                                                               |
| **Requirements** | The system shall log scan failures with timestamp, target, and failure reason. <br>The frontend shall surface failed scans to the user rather than only recording the failure on the backend. |
| **References**   | UC-05 View Scan History                                                                                                                                                                       |

## NFR-05

| **ID**           | NFR-05                                                                                                                                                                                                           |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Name**         | Maintainability - modular project structure                                                                                                                                                                      |
| **Summary**      | The codebase is organized so each functional area can be developed, tested, and modified independently.                                                                                                          |
| **Rationale**    | With multiple team members owning different areas, a modular and less tightly coupled structure minimizes merge conflicts and improves maintainability.                                                          |
| **Requirements** | The repository shall maintain separate top-level directories or modules per component. <br>Components shall communicate through defined interfaces, such as APIs, service functions, or defined data structures. |
| **References**   | UC-02 Start Network Scan                                                                                                                                                                                         |

## NFR-06

| **ID**           | NFR-06                                                                                                                                                                      |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Name**         | Compatibility - Ubuntu-based testing environment                                                                                                                            |
| **Summary**      | The backend and scanning components must run correctly on Ubuntu Linux, matching the team's test/deployment environment.                                                    |
| **Rationale**    | Linux is commonly used for networking and cybersecurity tools and is appropriate for a VM-based project test environment.                                                   |
| **Requirements** | NetSecure components shall be tested and confirmed working on the team's selected Ubuntu version. <br>The selected Ubuntu version shall be documented before final testing. |
| **References**   | UC-01 Login, UC-02 Start Network Scan                                                                                                                                       |

# 10\. Requirements Traceability Matrix

This matrix connects requirements to the use cases they support.

| **Requirement** | **Related Use Case(s)**    |
| --------------- | -------------------------- |
| **FR-01**       | UC-02                      |
| **FR-02**       | UC-02                      |
| **FR-03**       | UC-02, UC-03, UC-04, UC-05 |
| **FR-04**       | UC-03, UC-04, UC-05        |
| **FR-05**       | UC-03, UC-04, UC-05        |
| **FR-06**       | UC-03, UC-04, UC-05        |
| **NFR-01**      | UC-03, UC-04               |
| **NFR-02**      | UC-02                      |
| **NFR-03**      | UC-03, UC-04, UC-05        |
| **NFR-04**      | UC-05                      |
| **NFR-05**      | UC-02                      |
| **NFR-06**      | UC-01, UC-02               |

# 11\. Open Decisions and Assumptions

The updated presentation resolves the major use cases for View Security Threats and View Scan History. The following items remain open or should be confirmed by the team before implementation begins:

- Final backend framework selection: Flask or Django.
- Final frontend styling framework selection: Bootstrap or Tailwind CSS.
- Exact Ubuntu version for the testing environment.
- Exact severity scale names and colors for security findings.
- Final decision on whether scans will run through synchronous requests, background tasks, or another scan job approach.
- Final account model for users and administrators.