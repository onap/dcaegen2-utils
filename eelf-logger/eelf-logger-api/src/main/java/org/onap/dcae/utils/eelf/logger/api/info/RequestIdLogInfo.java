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
 * Captures fields required for logging request information
 *
 * @author Rajiv Singla
 */
public interface RequestIdLogInfo extends LogInfo {

    /**
     * Required field containing requestID which uniquely that identifies a single transaction request within the EELF
     * platform. Its value is conforms to RFC4122 UUID. The requestID value is passed using a REST API from one
     * EELF component to another via HTTP Headers named X-RequestID
     * <p>
     * <b>724229c0-9945-11e5-bcde-0002a5d5c51b:1234</b>
     * </p>
     * If receiving a composite requestID value, e.g. something of the form UUID-1:UUID-2, the receiving component
     * should only use the UUID-1 portion (i.e. remove the “:” and any trailing suffix, e.g. UUID-2) as the requestID
     * field value for its log files.
     *
     * @return requestID which uniquely that identifies a single transaction request within the EELF
     */
    String getRequestId();

}
