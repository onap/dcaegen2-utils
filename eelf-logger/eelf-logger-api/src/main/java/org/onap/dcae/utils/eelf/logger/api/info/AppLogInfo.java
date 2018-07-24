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
 *  Captures information about application which is doing the logging. All app log fields must remain same for
 *  the whole duration of the application once its instance is created.
 *
 * @author Rajiv Singla
 */
public interface AppLogInfo extends LogInfo {

    /**
     * Required field contains UUID which identifies this service instance inside an inventory management system
     * (e.g. A&AI) to reference/manage this service as a unit
     *
     * @return remote VM Name or service the request is acting upon.
     */
    String getServiceInstanceID();

    /**
     * Required field contains a universally unique identifier used to differentiate between multiple instances of
     * the same (named), log writing service/application. Its value is set at instance creation time (and read by it,
     * e.g. at start/initialization time from the environment).  This value should be picked up by the component
     * instance from its configuration file and subsequently used to enable differentiating log records created by
     * multiple, locally load balanced EELF component or sub component instances that are otherwise identically
     * configured.
     *
     * @return instance UUID
     */
    String getInstanceUUID();

    /**
     * Optional field contains VM Name where app is deployed.
     * DCAE sub components should populate this field but it can be empty if
     * determined that its value can be added by the log files collecting agent itself (e.g. Splunk).
     * <p>
     * <b> Example: zlpcsan3cacoll00.f8c8e6.san3.tci.att.com</b>
     * </p>
     *
     * @return virtual server name
     */
    String getVirtualServerName();

    /**
     * Optional field contains the logging component host server’s IP address.
     * <p>
     * <b>Example: 135.25.186.125</b>
     * </p>
     *
     * @return server ip address
     */
    String getServerIPAddress();

    /**
     * Required field for VM's fully qualified domain name or hosting machine fully qualified domain name.
     * <p>
     * <b> Example: zlpcsan3cacoll00.f8c8e6.san3.tci.att.com</b>
     * </p>
     *
     * @return server host fully qualified domain name
     */
    String getServerFQDN();


    /**
     * Contains default values for {@link AppLogInfo}
     */
    interface Defaults {

        String DEFAULT_SERVICE_INSTANCE_ID = "UNKNOWN_INSTANCE_ID";

        String DEFAULT_INSTANCE_UUID = "";

        String DEFAULT_VIRTUAL_SERVER_NAME = "";

        String DEFAULT_SERVER_IP_ADDRESS = "UNKNOWN_IP_ADDRESS";

        String DEFAULT_SERVER_FQDN = "UNKNOWN_SERVER_FQDN";

    }


}
