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

import org.junit.Test;
import org.onap.dcae.utils.eelf.logger.api.log.EELFLogFactory;
import org.onap.dcae.utils.eelf.logger.api.log.EELFLogger;
import org.onap.dcae.utils.eelf.logger.api.spec.DebugLogSpec;
import org.onap.dcae.utils.eelf.logger.logback.BaseLogbackUnitTest;
import org.onap.dcae.utils.eelf.logger.logback.EELFLoggerDefaults;
import org.onap.dcae.utils.eelf.logger.model.spec.DebugLogSpecImpl;


/**
 * Test for Debug log implementation.
 *
 * @author Rajiv Singla
 */
public class DebugLogImplTest extends BaseLogbackUnitTest {

    private static final EELFLogger LOG = EELFLogFactory.getLogger(DebugLogImplTest.class);

    @Test
    public void debugLoggerTest() throws Exception {

        LOG.debugLog().debug("Test DebugLog debug message: {}",
                getTestDebugLogSpec(), getTestOptionalLogSpec(), "debugArg");

        final DebugLogSpec emptyDebugLog = new DebugLogSpecImpl(null);

        LOG.debugLog().debug("Test Empty DebugLog debug message.", emptyDebugLog,
                EELFLoggerDefaults.DEFAULT_OPTIONAL_LOG_SPEC);

    }

}
