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

package org.onap.dcae.utils.eelf.logger.model.spec;

import lombok.AllArgsConstructor;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.ToString;
import lombok.experimental.Delegate;
import lombok.experimental.Wither;
import org.onap.dcae.utils.eelf.logger.api.info.ErrorLogInfo;
import org.onap.dcae.utils.eelf.logger.api.info.RequestIdLogInfo;
import org.onap.dcae.utils.eelf.logger.api.info.ServiceLogInfo;
import org.onap.dcae.utils.eelf.logger.api.info.TargetServiceLogInfo;
import org.onap.dcae.utils.eelf.logger.api.spec.ErrorLogSpec;


/**
 * Concrete model implementation for {@link ErrorLogSpec}
 *
 * @author Rajiv Singla
 */
@Getter
@AllArgsConstructor
@EqualsAndHashCode
@ToString
@Wither
public class ErrorLogSpecImpl implements ErrorLogSpec {

    private static final long serialVersionUID = 1L;

    @Delegate(types = RequestIdLogInfo.class)
    private RequestIdLogInfo requestIdLogInfo;

    @Delegate(types = ServiceLogInfo.class)
    private ServiceLogInfo serviceLogInfo;

    @Delegate(types = TargetServiceLogInfo.class)
    private TargetServiceLogInfo targetServiceLogInfo;

    @Delegate(types = ErrorLogInfo.class)
    private ErrorLogInfo errorLogInfo;

}
