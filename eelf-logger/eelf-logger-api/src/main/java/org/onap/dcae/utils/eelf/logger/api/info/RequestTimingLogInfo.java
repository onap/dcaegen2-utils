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

import java.util.Date;

/**
 * Captures Logging fields required for request timing related information
 *
 * @author Rajiv Singla
 */
public interface RequestTimingLogInfo extends LogInfo {

    /**
     * Required field containing creationTimestamp when the request processing started.
     * The value should be represented in UTC and formatted according to ISO 8601.
     * <p>
     * <b>Example: 2015-06-03T13:21:58+00:00</b>
     * </p>
     *
     * @return request activity begin creationTimestamp
     */
    Date getBeginTimestamp();


    /**
     * Required field containing creationTimestamp when the request processed stopped.
     * The value should be represented in UTC and formatted according to ISO 8601.
     * <p>
     * <b>Example: 2015-06-03T13:21:58+00:00</b>
     * </p>
     *
     * @return request activity end creationTimestamp
     */
    Date getEndTimestamp();


    /**
     * Required field contains the elapsed time to complete processing of an API call or transaction request (e.g.,
     * processing of a message that was received). This value should be the difference between EndTimestamp and
     * BeginTimestamp fields and should be expressed in milliseconds.
     *
     * @return request processing elapsed time in milliseconds
     */
    Long getElapsedTime();

}
