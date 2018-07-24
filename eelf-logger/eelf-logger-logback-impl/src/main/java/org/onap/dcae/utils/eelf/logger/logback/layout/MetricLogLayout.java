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

package org.onap.dcae.utils.eelf.logger.logback.layout;

import ch.qos.logback.classic.spi.ILoggingEvent;
import ch.qos.logback.core.LayoutBase;
import org.onap.dcae.utils.eelf.logger.api.info.LogLevelCategory;
import org.onap.dcae.utils.eelf.logger.api.spec.AppLogSpec;
import org.onap.dcae.utils.eelf.logger.api.spec.MetricLogSpec;
import org.onap.dcae.utils.eelf.logger.api.spec.OptionalLogSpec;

import static org.onap.dcae.utils.eelf.logger.logback.utils.LogUtils.createLogMessageString;
import static org.onap.dcae.utils.eelf.logger.logback.utils.LogUtils.formatDate;
import static org.onap.dcae.utils.eelf.logger.logback.utils.LogUtils.getAppLogSpec;
import static org.onap.dcae.utils.eelf.logger.logback.utils.LogUtils.getLogLevelCategory;
import static org.onap.dcae.utils.eelf.logger.logback.utils.LogUtils.getLoggerClass;
import static org.onap.dcae.utils.eelf.logger.logback.utils.LogUtils.getMetricLogSpec;
import static org.onap.dcae.utils.eelf.logger.logback.utils.LogUtils.getOptionalLogSpec;

/**
 * Metric Log Layout generates log messages as per EELF Metric Log Specifications
 *
 * @author Rajiv Singla
 */
public class MetricLogLayout extends LayoutBase<ILoggingEvent> {

    @Override
    public String doLayout(final ILoggingEvent event) {

        final AppLogSpec appLogSpec = getAppLogSpec();
        final LogLevelCategory logLevelCategory = getLogLevelCategory();
        final Class<?> loggerClass = getLoggerClass();
        final OptionalLogSpec optionalLogSpec = getOptionalLogSpec(loggerClass, logLevelCategory);
        final MetricLogSpec metricLogSpec = getMetricLogSpec();

        final String beginTimestamp = formatDate(metricLogSpec.getBeginTimestamp());
        final String endTimestamp = formatDate(metricLogSpec.getEndTimestamp());

        final String[] metricLogValues = {
                beginTimestamp,
                endTimestamp,
                metricLogSpec.getRequestId(),
                appLogSpec.getServiceInstanceID(),
                event.getThreadName(),
                appLogSpec.getVirtualServerName(),
                metricLogSpec.getServiceName(),
                metricLogSpec.getPartnerName(),
                metricLogSpec.getTargetEntity(),
                metricLogSpec.getTargetServiceName(),
                optionalLogSpec.getStatusCode().name(),
                metricLogSpec.getResponseCode().toString(),
                metricLogSpec.getResponseDescription(),
                appLogSpec.getInstanceUUID(),
                logLevelCategory != null ? logLevelCategory.name() : "",
                optionalLogSpec.getAlertSeverity().getSeverityCode(),
                appLogSpec.getServerIPAddress(),
                metricLogSpec.getElapsedTime().toString(),
                appLogSpec.getServerFQDN(),
                metricLogSpec.getClientIPAddress(),
                optionalLogSpec.getClassName(),
                optionalLogSpec.getUnused(),
                optionalLogSpec.getProcessId(),
                metricLogSpec.getTargetVirtualEntity(),
                optionalLogSpec.getCustomField1(),
                optionalLogSpec.getCustomField2(),
                optionalLogSpec.getCustomField3(),
                optionalLogSpec.getCustomField4(),
                event.getFormattedMessage()
        };

        return createLogMessageString(metricLogValues);
    }
}
