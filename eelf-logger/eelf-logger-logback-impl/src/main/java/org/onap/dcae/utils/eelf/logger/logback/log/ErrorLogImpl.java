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
import org.onap.dcae.utils.eelf.logger.api.log.ErrorLog;
import org.onap.dcae.utils.eelf.logger.api.spec.ErrorLogSpec;
import org.onap.dcae.utils.eelf.logger.api.spec.OptionalLogSpec;
import org.slf4j.Logger;

import static org.onap.dcae.utils.eelf.logger.logback.utils.LogUtils.CUSTOM_MDC_MAP;
import static org.onap.dcae.utils.eelf.logger.logback.utils.LogUtils.ERROR_LOG_MARKER;
import static org.onap.dcae.utils.eelf.logger.logback.utils.LogUtils.ERROR_LOG_SPEC_KEY;
import static org.onap.dcae.utils.eelf.logger.logback.utils.LogUtils.LOGGER_CLASS_KEY;
import static org.onap.dcae.utils.eelf.logger.logback.utils.LogUtils.LOG_LEVEL_CATEGORY_KEY;
import static org.onap.dcae.utils.eelf.logger.logback.utils.LogUtils.OPTIONAL_LOG_SPEC_KEY;
import static org.onap.dcae.utils.eelf.logger.logback.utils.LogUtils.logWithLogLevel;


/**
 * Error Log Logback Implementation
 *
 * @author Rajiv Singla
 */
public class ErrorLogImpl implements ErrorLog {

    private final Logger logger;
    private final Class<?> clazz;

    public ErrorLogImpl(final Logger logger, final Class<?> clazz) {
        this.logger = logger;
        this.clazz = clazz;
    }

    @Override
    public void log(final LogLevelCategory logLevelCategory, final String message, final ErrorLogSpec errorLogSpec,
                    final OptionalLogSpec optionalLogSpec, final String... args) {

        // if error log spec or log level category is null throw an exception
        if (errorLogSpec == null || logLevelCategory == null) {
            throw new IllegalArgumentException("Error Log Spec and Log level category must not be null");
        }

        // required fields
        CUSTOM_MDC_MAP.put(LOG_LEVEL_CATEGORY_KEY, logLevelCategory);
        CUSTOM_MDC_MAP.put(ERROR_LOG_SPEC_KEY, errorLogSpec);
        CUSTOM_MDC_MAP.put(LOGGER_CLASS_KEY, clazz);
        // optional fields
        CUSTOM_MDC_MAP.put(OPTIONAL_LOG_SPEC_KEY, optionalLogSpec);

        // log with normalized log level category
        logWithLogLevel(logLevelCategory, logger, ERROR_LOG_MARKER, message, args);

        // clean up
        CUSTOM_MDC_MAP.remove(LOG_LEVEL_CATEGORY_KEY);
        CUSTOM_MDC_MAP.remove(ERROR_LOG_SPEC_KEY);
        CUSTOM_MDC_MAP.remove(LOGGER_CLASS_KEY);
        CUSTOM_MDC_MAP.remove(OPTIONAL_LOG_SPEC_KEY);
    }

    @Override
    public void log(final LogLevelCategory logLevelCategory, final String message, final ErrorLogSpec errorLogSpec,
                    final String... args) {
        log(logLevelCategory, message, errorLogSpec, null, args);
    }

    @Override
    public void error(final String message, final ErrorLogSpec errorLogSpec, final OptionalLogSpec optionalLogSpec,
                      final String... args) {
        log(LogLevelCategory.ERROR, message, errorLogSpec, null, args);
    }

    @Override
    public void error(final String message, final ErrorLogSpec errorLogSpec, final String... args) {
        error(message, errorLogSpec, null, args);
    }

    @Override
    public void warn(final String message, final ErrorLogSpec errorLogSpec, final OptionalLogSpec optionalLogSpec,
                     final String... args) {
        log(LogLevelCategory.WARN, message, errorLogSpec, null, args);
    }

    @Override
    public void warn(final String message, final ErrorLogSpec errorLogSpec, final String... args) {
        warn(message, errorLogSpec, null, args);
    }
}
