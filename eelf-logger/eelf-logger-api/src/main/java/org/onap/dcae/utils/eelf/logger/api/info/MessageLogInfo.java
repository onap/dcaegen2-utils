/*
 * ================================================================================
 * Copyright (c) 2017 AT&T Intellectual Property. All rights reserved.
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
 * ECOMP is a trademark and service mark of AT&T Intellectual Property.
 */

package org.onap.dcae.utils.eelf.logger.api.info;

import java.util.Date;

/**
 * Captures fields required for message level logging. These fields are mostly derived fields. For example: creation
 * timestamp can be auto generated based on system time, {@link RequestStatusCode} and {@link NagiosAlertLevel} can be
 * derived based on {@link LogLevelCategory}
 *
 * @author Rajiv Singla
 */
public interface MessageLogInfo extends LogInfo {


    /**
     * Required field to capture when the message was created
     * The value should be represented in UTC and formatted according to ISO 8601.
     * <p>
     * <b>Example: 2015-06-03T13:21:58+00:00</b>
     * </p>
     *
     * @return message creation creationTimestamp
     */
    Date getCreationTimestamp();

    /**
     * Required field contains a value of COMPLETE or ERROR to indicate high level success or failure of the
     * request related activities.
     *
     * @return value to indicate high level success or failure of the request related activities
     */
    RequestStatusCode getStatusCode();


    /**
     * Optional field for Nagios monitoring/alerting severity code
     *
     * @return nagios monitoring/alerting severity code
     */
    NagiosAlertLevel getAlertSeverity();


}
