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
 * Capture field required to log details about code which is generating the log message.
 * <p>
 * <b>NOTE: When using a logging framework(e.g. logback) implementation these fields may be automatically deduced - so
 * settings these fields is not required by the application and even if application sets these fields the logging
 * framework may ignore it
 * </b>
 * </p>
 *
 * @author Rajiv Singla
 */
public interface CodeLogInfo extends LogInfo {


    /**
     * Optional field used if wanting to trace processing of a request over a number of sub-components of a single EELF
     * component. It should be preceded by a log record that establishes its chaining back to the corresponding
     * requestID.
     *
     * @return thread ID used to trace processing of request over number of sub-components of single EELF Component.
     */
    String getThreadId();


    /**
     * Optional field: If available for OO programing languages that support this concept. This is the name of the
     * class that has caused the log record to be created.
     *
     * @return name of the class that has the caused the log record to be created
     */
    String getClassName();


}
