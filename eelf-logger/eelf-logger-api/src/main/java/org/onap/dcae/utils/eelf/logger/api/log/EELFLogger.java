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

package org.onap.dcae.utils.eelf.logger.api.log;

/**
 * EELF Logger is main abstraction which applications use to log EELF Compliant log messages
 *
 * @author Rajiv Singla
 */
public interface EELFLogger {

    /**
     * Provides Audit Log
     *
     * @return Audit log
     */
    AuditLog auditLog();


    /**
     * Provides Metric Log
     *
     * @return metric log
     */
    MetricLog metricLog();

    /**
     * Provides Error Log
     *
     * @return error log
     */
    ErrorLog errorLog();


    /**
     * Provides Debug Log
     *
     * @return debug log
     */
    DebugLog debugLog();

    /**
     * Provides logging context
     *
     * @return logging context
     */
    EELFLoggerContext loggingContext();


}
