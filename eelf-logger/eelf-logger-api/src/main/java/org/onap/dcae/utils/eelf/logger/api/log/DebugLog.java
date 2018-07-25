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

package org.onap.dcae.utils.eelf.logger.api.log;

import org.onap.dcae.utils.eelf.logger.api.info.LogLevelCategory;
import org.onap.dcae.utils.eelf.logger.api.spec.DebugLogSpec;
import org.onap.dcae.utils.eelf.logger.api.spec.OptionalLogSpec;

/**
 * Debug Log captures all log levels supported by debug specifications.
 * <p>
 * <b>NOTE: DEBUG Log is optional as per EELF Specifications</b>
 *
 * @author Rajiv Singla
 */
public interface DebugLog {

    /**
     * Logs debug message with provided {@link LogLevelCategory}
     *
     * @param logLevelCategory log level category
     * @param message log message
     * @param debugLogSpec debug log spec
     * @param optionalLogSpec optional log spec
     * @param args argument values for log message interpolation
     */
    void log(LogLevelCategory logLevelCategory, String message, DebugLogSpec debugLogSpec,
             OptionalLogSpec optionalLogSpec, String... args);

    /**
     * Logs debug message with provided {@link LogLevelCategory} and with default {@link OptionalLogSpec}
     *
     * @param logLevelCategory log level category
     * @param message log message
     * @param debugLogSpec debug log spec
     * @param args argument values for log message interpolation
     */
    void log(LogLevelCategory logLevelCategory, String message, DebugLogSpec debugLogSpec, String... args);


    /**
     * Logs debug message with provided DEBUG {@link LogLevelCategory}
     *
     * @param message log message
     * @param debugLogSpec debug log spec
     * @param args argument values for log message interpolation
     */
    void debug(String message, DebugLogSpec debugLogSpec, OptionalLogSpec optionalLogSpec, String... args);

    /**
     * Logs debug message with provided DEBUG {@link LogLevelCategory} and with default {@link OptionalLogSpec}
     *
     * @param message log message
     * @param debugLogSpec debug log spec
     * @param args argument values for log message interpolation
     */
    void debug(String message, DebugLogSpec debugLogSpec, String... args);

}
