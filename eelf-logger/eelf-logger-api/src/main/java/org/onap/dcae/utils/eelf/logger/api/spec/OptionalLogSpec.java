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

import org.onap.dcae.utils.eelf.logger.api.info.CodeLogInfo;
import org.onap.dcae.utils.eelf.logger.api.info.CustomFieldsLogInfo;
import org.onap.dcae.utils.eelf.logger.api.info.MessageLogInfo;
import org.onap.dcae.utils.eelf.logger.api.info.MiscLogInfo;

/**
 * Captures fields which are optional or derived from other fields
 *
 * @author Rajiv Singla
 */
public interface OptionalLogSpec extends
        // message fields are mostly auto generated or can be derived from other fields
        MessageLogInfo,
        // Code log info can be derived by the underlying logging framework or provided optionally by the app
        CodeLogInfo,
        // custom and misc log info are mostly optional
        CustomFieldsLogInfo, MiscLogInfo {
}
