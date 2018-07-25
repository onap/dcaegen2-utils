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

package org.onap.dcae.utils.eelf.logger.logback.layout;

import ch.qos.logback.classic.spi.ILoggingEvent;
import ch.qos.logback.core.LayoutBase;
import org.onap.dcae.utils.eelf.logger.logback.utils.LogUtils;
import org.slf4j.Marker;

/**
 * Console layout is used to log messages on the console for debugging purposes.
 *
 * @author Rajiv Singla
 */
public class ConsoleLayout extends LayoutBase<ILoggingEvent> {

    private static final MetricLogLayout METRIC_LOG_LAYOUT = new MetricLogLayout();
    private static final AuditLogLayout AUDIT_LOG_LAYOUT = new AuditLogLayout();
    private static final ErrorLogLayout ERROR_LOG_LAYOUT = new ErrorLogLayout();
    private static final DebugLogLayout DEBUG_LOG_LAYOUT = new DebugLogLayout();

    @Override
    public String doLayout(final ILoggingEvent event) {

        final Marker eventMarker = event.getMarker();

        if (eventMarker.equals(LogUtils.AUDIT_LOG_MARKER)) {
            return AUDIT_LOG_LAYOUT.doLayout(event);
        } else if (eventMarker.equals(LogUtils.METRIC_LOG_MARKER)) {
            return METRIC_LOG_LAYOUT.doLayout(event);
        } else if (eventMarker.equals(LogUtils.ERROR_LOG_MARKER)) {
            return ERROR_LOG_LAYOUT.doLayout(event);
        } else if (eventMarker.equals(LogUtils.DEBUG_LOG_MARKER)) {
            return DEBUG_LOG_LAYOUT.doLayout(event);
        }

        return "Console Layout not defined for Marker: " + eventMarker;
    }
}
