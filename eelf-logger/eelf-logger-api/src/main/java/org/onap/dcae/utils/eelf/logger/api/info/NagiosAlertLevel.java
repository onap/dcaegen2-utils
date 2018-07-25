/*
 * ================================================================================
 * Copyright (c) 2018 AT&T Intellectual Property. All rights reserved.
 * ================================================================================
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * ============LICENSE_END=========================================================
 *
 */

package org.onap.dcae.utils.eelf.logger.api.info;

/**
 * Enum for Nagios monitoring/alerting codes as per table below.
 * <p>
 * <table cellspacing=0 border=1>
 * <tr><th>Return Code</th><th>Service State</th><th>Host State</th></tr>
 * <tr><td>0</td><td>OK</td><td>UP</td></tr>
 * <tr><td>1</td><td>WARNING</td><td>UP or DOWN/UNREACHABLE*</td></tr>
 * <tr><td>2</td><td>CRITICAL</td><td>DOWN/UNREACHABLE</td></tr>
 * <tr><td>3</td><td>UNKNOWN</td><td>DOWN/UNREACHABLE</td></tr>
 * </table>
 *
 * @author Rajiv Singla
 */
public enum NagiosAlertLevel implements LogInfo {

    OK("0"),
    WARNING("1"),
    CRITICAL("2"),
    UNKNOWN("3");

    private String severityCode;

    NagiosAlertLevel(final String severityCode) {
        this.severityCode = severityCode;
    }

    public String getSeverityCode() {
        return severityCode;
    }

}
