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

import java.io.Serializable;
import java.util.List;

/**
 * A resolver is used to resolve properties
 *
 * @author Rajiv Singla
 */
public interface PropertyResolver extends Serializable {

    /**
     * Returns resolved property value
     *
     * @param propertyNames names under which property can be found
     *
     * @return property value
     */
    String resolve(List<String> propertyNames);

}
