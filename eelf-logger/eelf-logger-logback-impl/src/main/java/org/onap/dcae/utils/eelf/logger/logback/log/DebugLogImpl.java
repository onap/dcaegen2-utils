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

package org.onap.dcae.utils.eelf.logger.logback.log;


import org.onap.dcae.utils.eelf.logger.api.info.LogLevelCategory;
import org.onap.dcae.utils.eelf.logger.api.log.DebugLog;
import org.onap.dcae.utils.eelf.logger.api.spec.DebugLogSpec;
import org.onap.dcae.utils.eelf.logger.api.spec.OptionalLogSpec;
import org.onap.dcae.utils.eelf.logger.logback.utils.LogUtils;
import org.slf4j.Logger;


/**
 * Debug Log Logback Implementation
 *
 * @author Rajiv Singla
 */
public class DebugLogImpl implements DebugLog {

    private final Logger logger;
    private final Class<?> clazz;

    public DebugLogImpl(final Logger logger, final Class<?> clazz) {
        this.logger = logger;
        this.clazz = clazz;
    }

    @Override
    public void log(final LogLevelCategory logLevelCategory, final String message, final DebugLogSpec debugLogSpec,
                    final OptionalLogSpec optionalLogSpec, final String... args) {

        // if log level category is null throw an exception
        if (logLevelCategory == null) {
            throw new IllegalArgumentException("Log level category must not be null");
        }

        LogUtils.CUSTOM_MDC_MAP.put(LogUtils.LOG_LEVEL_CATEGORY_KEY, logLevelCategory);
        LogUtils.CUSTOM_MDC_MAP.put(LogUtils.DEBUG_LOG_SPEC_KEY, debugLogSpec);
        LogUtils.CUSTOM_MDC_MAP.put(LogUtils.LOGGER_CLASS_KEY, clazz);
        // optional fields
        LogUtils.CUSTOM_MDC_MAP.put(LogUtils.OPTIONAL_LOG_SPEC_KEY, optionalLogSpec);

        // log with normalized log level category
        LogUtils.logWithLogLevel(logLevelCategory, logger, LogUtils.DEBUG_LOG_MARKER, message, args);

        // clean up
        LogUtils.CUSTOM_MDC_MAP.remove(LogUtils.LOG_LEVEL_CATEGORY_KEY);
        LogUtils.CUSTOM_MDC_MAP.remove(LogUtils.DEBUG_LOG_SPEC_KEY);
        LogUtils.CUSTOM_MDC_MAP.remove(LogUtils.LOGGER_CLASS_KEY);
        LogUtils.CUSTOM_MDC_MAP.remove(LogUtils.OPTIONAL_LOG_SPEC_KEY);

    }

    @Override
    public void log(final LogLevelCategory logLevelCategory, final String message, final DebugLogSpec debugLogSpec,
                    final String... args) {
        log(logLevelCategory, message, debugLogSpec, null, args);
    }

    @Override
    public void debug(final String message, final DebugLogSpec debugLogSpec, final OptionalLogSpec optionalLogSpec,
                      final String... args) {
        log(LogLevelCategory.DEBUG, message, debugLogSpec, optionalLogSpec, args);
    }

    @Override
    public void debug(final String message, final DebugLogSpec debugLogSpec, final String... args) {
        debug(message, debugLogSpec, null, args);
    }
}
