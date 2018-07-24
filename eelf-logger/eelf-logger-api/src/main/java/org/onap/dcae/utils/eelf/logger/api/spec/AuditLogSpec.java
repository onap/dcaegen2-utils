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

package org.onap.dcae.utils.eelf.logger.api.spec;


import org.onap.dcae.utils.eelf.logger.api.info.RequestIdLogInfo;
import org.onap.dcae.utils.eelf.logger.api.info.RequestTimingLogInfo;
import org.onap.dcae.utils.eelf.logger.api.info.ResponseLogInfo;
import org.onap.dcae.utils.eelf.logger.api.info.ServiceLogInfo;

/**
 * Captures fields required for EELF Audit Log Specification.
 *
 * @author Rajiv Singla
 */
public interface AuditLogSpec extends
        // request id must be preset for all log specifications
        RequestIdLogInfo,
        // duration related fields
        RequestTimingLogInfo,
        // app acting as a service fields
        ServiceLogInfo, ResponseLogInfo {


}
