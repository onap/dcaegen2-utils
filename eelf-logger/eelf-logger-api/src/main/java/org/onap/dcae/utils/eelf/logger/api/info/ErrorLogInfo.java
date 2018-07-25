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
 * Captures fields required to log error related information
 *
 * @author Rajiv Singla
 */
public interface ErrorLogInfo extends LogInfo {


    /**
     * Required field contains an error code representing the error condition. The codes can be chose by
     * the logging application but they should adhere to the guidelines embodied in the table below:
     * <table summary="Error Codes" cellspacing=0 border=1>
     * <tr>
     * <td style=min-width:50px>Error type</td>
     * <td style=min-width:50px>Notes</td>
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
     * @return error Code
     */
    Integer getErrorCode();


    /**
     * Required field contains a human readable description of the error condition.
     *
     * @return human readable description of the error condition
     */
    String getErrorDescription();

}
