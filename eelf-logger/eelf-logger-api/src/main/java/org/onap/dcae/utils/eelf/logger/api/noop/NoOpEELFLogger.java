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

package org.onap.dcae.utils.eelf.logger.api.noop;


import org.onap.dcae.utils.eelf.logger.api.log.AuditLog;
import org.onap.dcae.utils.eelf.logger.api.log.DebugLog;
import org.onap.dcae.utils.eelf.logger.api.log.EELFLogger;
import org.onap.dcae.utils.eelf.logger.api.log.EELFLoggerContext;
import org.onap.dcae.utils.eelf.logger.api.log.ErrorLog;
import org.onap.dcae.utils.eelf.logger.api.log.MetricLog;

/**
 * A no operation implementation of {@link EELFLogger}
 *
 * @author Rajiv Singla
 */
public class NoOpEELFLogger implements EELFLogger {

    private static final AuditLog NO_OP_AUDIT_LOG = new NoOpAuditLog();
    private static final MetricLog NO_OP_METRIC_LOG = new NoOpMetricLog();
    private static final ErrorLog NO_OP_ERROR_LOG = new NoOpErrorLog();
    private static final DebugLog NO_OP_DEBUG_LOG = new NoOpDebugLog();

    private static final NoOpEELFLogger NO_OP_EELF_LOGGER = new NoOpEELFLogger();

    private NoOpEELFLogger() {
        // private constructor
    }

    public static NoOpEELFLogger getInstance() {
        return NO_OP_EELF_LOGGER;
    }

    @Override
    public AuditLog auditLog() {
        return NO_OP_AUDIT_LOG;
    }

    @Override
    public MetricLog metricLog() {
        return NO_OP_METRIC_LOG;
    }

    @Override
    public ErrorLog errorLog() {
        return NO_OP_ERROR_LOG;
    }

    @Override
    public DebugLog debugLog() {
        return NO_OP_DEBUG_LOG;
    }

    @Override
    public EELFLoggerContext loggingContext() {
        return null;
    }

}
