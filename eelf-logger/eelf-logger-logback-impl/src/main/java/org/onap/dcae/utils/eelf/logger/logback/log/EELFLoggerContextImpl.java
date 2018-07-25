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

package org.onap.dcae.utils.eelf.logger.logback.log;

import org.onap.dcae.utils.eelf.logger.api.log.EELFLoggerContext;
import org.onap.dcae.utils.eelf.logger.api.spec.AppLogSpec;
import org.onap.dcae.utils.eelf.logger.model.spec.AppLogSpecImpl;

import static org.onap.dcae.utils.eelf.logger.logback.EELFLoggerDefaults.DEFAULT_APP_LOG_INFO;
import static org.onap.dcae.utils.eelf.logger.logback.utils.LogUtils.APP_LOG_SPEC_KEY;
import static org.onap.dcae.utils.eelf.logger.logback.utils.LogUtils.CUSTOM_MDC_MAP;


/**
 * Default EELF Logger Context which contains EELF Specs which are usually constant for entire life cycle of the
 * application
 *
 * @author Rajiv Singla
 */
public class EELFLoggerContextImpl implements EELFLoggerContext {

    @Override
    public AppLogSpec getAppLogSpec() {
        return CUSTOM_MDC_MAP.get(APP_LOG_SPEC_KEY) == null ? null : (AppLogSpec) CUSTOM_MDC_MAP.get(APP_LOG_SPEC_KEY);
    }

    @Override
    public void setAppLogSpec(final AppLogSpec appLogSpec) {
        if (appLogSpec == null) {
            CUSTOM_MDC_MAP.put(APP_LOG_SPEC_KEY, new AppLogSpecImpl(DEFAULT_APP_LOG_INFO));
        } else {
            CUSTOM_MDC_MAP.put(APP_LOG_SPEC_KEY, appLogSpec);
        }
    }

    @Override
    public boolean isInitialized() {
        return CUSTOM_MDC_MAP.get(APP_LOG_SPEC_KEY) == null;
    }
}
