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

package org.onap.dcae.utils.eelf.logger.api.info;

/**
 * Captures optional / deprecated fields that can be populated as per EELF Logging Requirements
 *
 * @author Rajiv Singla
 */
public interface MiscLogInfo extends LogInfo {

    /**
     * Optional field that can can be used to capture the flow of a transaction through the system by
     * indicating the components and operations involved in processed. If present, it can be denoted by a comma
     * separated list of components and applications.
     *
     * @return list of comma separated components and operations involved in processing
     */
    String getProcessId();

    /**
     * This field is deprecated and should be left empty.
     *
     * @return deprecated field value - should be empty
     */
    String getUnused();

}
