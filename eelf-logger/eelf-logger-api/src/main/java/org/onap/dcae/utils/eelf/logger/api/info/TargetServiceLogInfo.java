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

package org.onap.dcae.utils.eelf.logger.api.info;

/**
 * Captures fields for logging application which is calling an external/target service
 *
 * @author Rajiv Singla
 */
public interface TargetServiceLogInfo extends LogInfo {

    /**
     * Required field containing name of EELF component/sub component or non-EELF entity which is invoked by the
     * logging application
     *
     * @return target entity name which is invoked by the logging application
     */
    String getTargetEntity();


    /**
     * Required field containing name of External API/operation activities invoked on {@link #getTargetEntity()}
     *
     * @return target service name invoked by the logging application
     */
    String getTargetServiceName();


    /**
     * Optional field containing target VNF or VM being acted upon by the logging application. This field contains the
     * virtual entity that is the target of the action for example the FQDN of the target virtual entity
     *
     * @return target Virtual Entity
     */
    String getTargetVirtualEntity();

}
