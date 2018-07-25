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
import org.onap.dcae.utils.eelf.logger.api.info.CodeLogInfo;
import org.onap.dcae.utils.eelf.logger.api.info.CustomFieldsLogInfo;
import org.onap.dcae.utils.eelf.logger.api.info.MessageLogInfo;
import org.onap.dcae.utils.eelf.logger.api.info.MiscLogInfo;
import org.onap.dcae.utils.eelf.logger.api.spec.OptionalLogSpec;


/**
 * Concrete model implementation for {@link OptionalLogSpec}
 *
 * @author Rajiv Singla
 */
@Getter
@AllArgsConstructor
@EqualsAndHashCode
@ToString
@Wither
public class OptionalLogSpecImpl implements OptionalLogSpec {

    private static final long serialVersionUID = 1L;

    @Delegate(types = MessageLogInfo.class)
    private MessageLogInfo messageLogInfo;

    @Delegate(types = CodeLogInfo.class)
    private CodeLogInfo codeLogInfo;

    @Delegate(types = CustomFieldsLogInfo.class)
    private CustomFieldsLogInfo customFieldsLogInfo;

    @Delegate(types = MiscLogInfo.class)
    private MiscLogInfo miscLogInfo;
}
