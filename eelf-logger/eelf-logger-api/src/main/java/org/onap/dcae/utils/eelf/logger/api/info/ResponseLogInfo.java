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
 * Captures field required for logging Response information
 *
 * @author Rajiv Singla
 */
public interface ResponseLogInfo extends LogInfo {

    /**
     * Required field contains application-specific response codes. While error codes are
     * application-specific, they
     * should conform categories mentioned in table below in order to provide consistency
     * <p>
     * <table cellspacing=0 border=1>
     * <tr>
     * <th style=min-width:50px><b>Error type</b></th>
     * <th style=min-width:50px><b>Notes</b></th>
     * </tr>
     * <tr>
     * <td style=min-width:50px>0</td>
     * <td style=min-width:50px>Success</td>
     * </tr>
     * <tr>
     * <td style=min-width:50px>100</td>
     * <td style=min-width:50px>Permission errors</td>
     * </tr>
     * <tr>
     * <td style=min-width:50px>200</td>
     * <td style=min-width:50px>Availability errors/Timeouts</td>
     * </tr>
     * <tr>
     * <td style=min-width:50px>300</td>
     * <td style=min-width:50px>Data errors</td>
     * </tr>
     * <tr>
     * <td style=min-width:50px>400</td>
     * <td style=min-width:50px>Schema errors</td>
     * </tr>
     * <tr>
     * <td style=min-width:50px>500</td>
     * <td style=min-width:50px>Business process errors</td>
     * </tr>
     * <tr>
     * <td style=min-width:50px>900</td>
     * <td style=min-width:50px>Unknown Errors</td>
     * </tr>
     * </table>
     *
     * @return application-specific error code
     */
    Integer getResponseCode();


    /**
     * Required field contains a human readable description of the {@link #getResponseCode()}.
     *
     * @return human readable description of the response code
     */
    String getResponseDescription();

}
