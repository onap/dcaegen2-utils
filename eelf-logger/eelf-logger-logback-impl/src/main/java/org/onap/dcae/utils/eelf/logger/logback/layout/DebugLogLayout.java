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
import org.onap.dcae.utils.eelf.logger.api.spec.DebugLogSpec;
import org.onap.dcae.utils.eelf.logger.api.spec.OptionalLogSpec;
import org.onap.dcae.utils.eelf.logger.logback.utils.LogUtils;


/**
 * @author Rajiv Singla
 */
public class DebugLogLayout extends LayoutBase<ILoggingEvent> {

    @Override
    public String doLayout(final ILoggingEvent event) {

        final LogLevelCategory logLevelCategory = LogUtils.getLogLevelCategory();
        final Class<?> loggerClass = LogUtils.getLoggerClass();
        final OptionalLogSpec optionalLogSpec = LogUtils.getOptionalLogSpec(loggerClass, logLevelCategory);

        final DebugLogSpec debugLogSpec = LogUtils.getDebugLogSpec();

        final String creationTimestamp = LogUtils.formatDate(optionalLogSpec.getCreationTimestamp());

        final String[] debugLogValues = {
                creationTimestamp,
                debugLogSpec.getRequestId(),
                event.getFormattedMessage()
        };

        return LogUtils.createLogMessageString(debugLogValues);
    }
}
