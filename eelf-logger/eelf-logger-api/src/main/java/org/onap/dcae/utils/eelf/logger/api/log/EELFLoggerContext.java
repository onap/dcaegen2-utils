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

package org.onap.dcae.utils.eelf.logger.api.log;


import org.onap.dcae.utils.eelf.logger.api.spec.AppLogSpec;

/**
 * EELF Logger Context contains fields are set during application creation time and are fixed for the entire
 * duration of the application lifetime
 *
 * @author Rajiv Singla
 */
public interface EELFLoggerContext {

    /**
     * Returns App Log Spec
     *
     * @return current app log spec
     */
    AppLogSpec getAppLogSpec();


    /**
     * Sets new App Log Spec
     *
     * @param appLogSpec new app log spec
     */
    void setAppLogSpec(AppLogSpec appLogSpec);


    /**
     * Returns true if logging context is already initialized
     *
     * @return true if logger context is already initialized
     */
    boolean isInitialized();

}
