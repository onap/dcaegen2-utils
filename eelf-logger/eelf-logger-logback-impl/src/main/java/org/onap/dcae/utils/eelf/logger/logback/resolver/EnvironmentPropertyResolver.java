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

package org.onap.dcae.utils.eelf.logger.logback.resolver;

import java.util.List;

/**
 * Looks up Property values inside HOST environment variables
 *
 * @author Rajiv Singla
 */
public class EnvironmentPropertyResolver implements PropertyResolver {

    private static final long serialVersionUID = 1L;

    @Override
    public String resolve(final List<String> propertyNames) {

        // check if system environment variables have property names set
        for (final String propertyName : propertyNames) {
            final String propertyValue = System.getenv(propertyName);
            if (propertyValue != null) {
                return propertyValue;
            }
        }

        return null;
    }
}
