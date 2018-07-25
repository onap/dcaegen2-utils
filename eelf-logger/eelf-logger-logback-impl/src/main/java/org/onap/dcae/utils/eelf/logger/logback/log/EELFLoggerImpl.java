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

package org.onap.dcae.utils.eelf.logger.logback.log;


import org.onap.dcae.utils.eelf.logger.api.log.AuditLog;
import org.onap.dcae.utils.eelf.logger.api.log.DebugLog;
import org.onap.dcae.utils.eelf.logger.api.log.EELFLogger;
import org.onap.dcae.utils.eelf.logger.api.log.EELFLoggerContext;
import org.onap.dcae.utils.eelf.logger.api.log.ErrorLog;
import org.onap.dcae.utils.eelf.logger.api.log.MetricLog;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * EELF Logger Logback Implementation
 *
 * @author Rajiv Singla
 */
public class EELFLoggerImpl implements EELFLogger {

    private Logger logger;
    private Class<?> clazz;

    public EELFLoggerImpl() {
        // no arg constructor required for Service Loader discovery
    }

    public EELFLoggerImpl(final Class<?> clazz) {
        logger = LoggerFactory.getLogger(clazz);
        this.clazz = clazz;
    }


    @Override
    public AuditLog auditLog() {
        return new AuditLogImpl(logger, clazz);
    }

    @Override
    public MetricLog metricLog() {
        return new MetricLogImpl(logger, clazz);
    }

    @Override
    public ErrorLog errorLog() {
        return new ErrorLogImpl(logger, clazz);
    }

    @Override
    public DebugLog debugLog() {
        return new DebugLogImpl(logger, clazz);
    }

    @Override
    public EELFLoggerContext loggingContext() {
        return new EELFLoggerContextImpl();
    }

    @Override
    public String toString() {
        return "EELF LOGBACK IMP";
    }
}
