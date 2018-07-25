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

package org.onap.dcae.utils.eelf.logger.model.spec;

import lombok.AllArgsConstructor;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.ToString;
import lombok.experimental.Delegate;
import lombok.experimental.Wither;
import org.onap.dcae.utils.eelf.logger.api.info.RequestIdLogInfo;
import org.onap.dcae.utils.eelf.logger.api.info.RequestTimingLogInfo;
import org.onap.dcae.utils.eelf.logger.api.info.ResponseLogInfo;
import org.onap.dcae.utils.eelf.logger.api.info.ServiceLogInfo;
import org.onap.dcae.utils.eelf.logger.api.spec.AuditLogSpec;


/**
 * Concrete model implementation for {@link AuditLogSpec}
 *
 * @author Rajiv Singla
 */
@Getter
@AllArgsConstructor
@EqualsAndHashCode
@ToString
@Wither
public class AuditLogSpecImpl implements AuditLogSpec {

    private static final long serialVersionUID = 1L;

    @Delegate(types = RequestIdLogInfo.class)
    private RequestIdLogInfo requestIdLogInfo;

    @Delegate(types = ServiceLogInfo.class)
    private ServiceLogInfo serviceLogInfo;

    @Delegate(types = RequestTimingLogInfo.class)
    private RequestTimingLogInfo requestTimingLogInfo;

    @Delegate(types = ResponseLogInfo.class)
    private ResponseLogInfo responseLogInfo;

}
