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
 * Captures information about logging fields for application acting as service and handling requests from other
 * applications
 *
 * @author Rajiv Singla
 */
public interface ServiceLogInfo extends LogInfo {

    /**
     * Required field contains the developer given name of the ecomp component's exposed api (~='method', function')
     * invoked. For example if the application is exposing a REST interface and exposing runtime metrics then the
     * service name can be: appName-getMetrics
     *
     * @return name of the API invoked by the application
     */
    String getServiceName();


    /**
     * Optional field contains the name of the client or user invoking the service.
     * It may be an application, user name or mech id.
     *
     * @return name of the client or user invoking the API if known
     */
    String getPartnerName();


    /**
     * Optional field contains requesting remote client application’s IP address. Use UNKNOWN or an empty string if not
     * available.
     *
     * @return remote client application’s IP address
     */
    String getClientIPAddress();


}



