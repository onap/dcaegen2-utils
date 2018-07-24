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


import org.onap.dcae.utils.eelf.logger.api.info.LogLevelCategory;
import org.onap.dcae.utils.eelf.logger.api.spec.ErrorLogSpec;
import org.onap.dcae.utils.eelf.logger.api.spec.OptionalLogSpec;

/**
 * @author Rajiv Singla
 */
public interface ErrorLog {

    /**
     * Logs error message with provided {@link LogLevelCategory}
     *
     * @param logLevelCategory log level category
     * @param message log message
     * @param errorLogSpec error log spec
     * @param optionalLogSpec optional log spec
     * @param args argument values for log message interpolation
     */
    void log(LogLevelCategory logLevelCategory, String message, ErrorLogSpec errorLogSpec,
             OptionalLogSpec optionalLogSpec, String... args);

    /**
     * Logs error message with provided {@link LogLevelCategory} and with default {@link OptionalLogSpec}
     *
     * @param logLevelCategory log level category
     * @param message log message
     * @param errorLogSpec error log spec
     * @param args argument values for log message interpolation
     */
    void log(LogLevelCategory logLevelCategory, String message, ErrorLogSpec errorLogSpec, String... args);


    /**
     * Logs error message with ERROR {@link LogLevelCategory}
     *
     * @param message log message
     * @param errorLogSpec error log spec
     * @param args argument values for log message interpolation
     */
    void error(String message, ErrorLogSpec errorLogSpec, OptionalLogSpec optionalLogSpec, String... args);

    /**
     * Logs error message with ERROR {@link LogLevelCategory} and with default {@link OptionalLogSpec}
     *
     * @param message log message
     * @param errorLogSpec error log spec
     * @param args argument values for log message interpolation
     */
    void error(String message, ErrorLogSpec errorLogSpec, String... args);


    /**
     * Logs error message with WARN {@link LogLevelCategory}
     *
     * @param message log message
     * @param errorLogSpec error log spec
     * @param args argument values for log message interpolation
     */
    void warn(String message, ErrorLogSpec errorLogSpec, OptionalLogSpec optionalLogSpec, String... args);

    /**
     * Logs error message with WARN {@link LogLevelCategory} and with default {@link OptionalLogSpec}
     *
     * @param message log message
     * @param errorLogSpec error log spec
     * @param args argument values for log message interpolation
     */
    void warn(String message, ErrorLogSpec errorLogSpec, String... args);


}
