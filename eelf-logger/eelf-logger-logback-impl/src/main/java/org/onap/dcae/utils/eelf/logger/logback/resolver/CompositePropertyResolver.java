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

import java.util.Arrays;
import java.util.List;

/**
 * A composite property resolver can look under different resolvers in order of given property resolvers
 *
 * @author Rajiv Singla
 */
public class CompositePropertyResolver implements PropertyResolver {

    private static final long serialVersionUID = 1L;

    private final List<PropertyResolver> propertyResolvers;

    public CompositePropertyResolver(PropertyResolver... propertyResolvers) {
        this.propertyResolvers = Arrays.asList(propertyResolvers);
    }

    @Override
    public String resolve(final List<String> propertyNames) {
        // resolver property in given resolvers in the same order they are defined
        for (PropertyResolver propertyResolver : propertyResolvers) {
            final String propertyValue = propertyResolver.resolve(propertyNames);
            if (propertyValue != null) {
                return propertyValue;
            }
        }

        return null;
    }

}
