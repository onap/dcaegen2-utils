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
import java.util.Map;
import java.util.Properties;

/**
 * Resolve System Properties passed in by -DpropertyName=propertyValue when invoking
 * via java command line arguments
 *
 * @author Rajiv Singla
 */
public class SystemPropertyResolver implements PropertyResolver {

    private static final long serialVersionUID = 1L;

    @Override
    public String resolve(final List<String> propertyNames) {

        // Get all system Properties
        final Properties systemProperties = System.getProperties();

        for (Map.Entry<Object, Object> systemEntries : systemProperties.entrySet()) {

            if (systemEntries.getKey() instanceof String) {
                final String systemKey = (String) systemEntries.getKey();

                // if system properties contain any of the property names - ignoring case then return its value
                for (String propertyName : propertyNames) {
                    if (propertyName.equalsIgnoreCase(systemKey)) {
                        return (String) systemEntries.getValue();
                    }
                }

            }
        }

        return null;
    }
}
