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

package org.onap.dcae.utils.eelf.logger.api.noop;


import org.onap.dcae.utils.eelf.logger.api.info.LogLevelCategory;
import org.onap.dcae.utils.eelf.logger.api.log.ErrorLog;
import org.onap.dcae.utils.eelf.logger.api.spec.ErrorLogSpec;
import org.onap.dcae.utils.eelf.logger.api.spec.OptionalLogSpec;

/**
 * A no operation implementation of Error Log
 *
 * @author Rajiv Singla
 */
public class NoOpErrorLog implements ErrorLog {

    @Override
    public void log(final LogLevelCategory logLevelCategory, final String message, final ErrorLogSpec errorLogSpec,
                    final OptionalLogSpec optionalLogSpec, final String... args) {
        // no operation
    }

    @Override
    public void log(final LogLevelCategory logLevelCategory, final String message, final ErrorLogSpec errorLogSpec,
                    final String... args) {
        // no operation
    }

    @Override
    public void error(final String message, final ErrorLogSpec errorLogSpec, final OptionalLogSpec optionalLogSpec,
                      final String... args) {
        // no operation
    }

    @Override
    public void error(final String message, final ErrorLogSpec errorLogSpec, final String... args) {
        // no operation
    }

    @Override
    public void warn(final String message, final ErrorLogSpec errorLogSpec, final OptionalLogSpec optionalLogSpec,
                     final String... args) {
        // no operation
    }

    @Override
    public void warn(final String message, final ErrorLogSpec errorLogSpec, final String... args) {
        // no operation
    }
}
