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

package org.onap.dcae.utils.eelf.logger.logback;


import org.onap.dcae.utils.eelf.logger.api.info.LogInfo;
import org.onap.dcae.utils.eelf.logger.model.info.AppLogInfoImpl;
import org.onap.dcae.utils.eelf.logger.model.info.CustomFieldsLogInfoImpl;
import org.onap.dcae.utils.eelf.logger.model.info.ErrorLogInfoImpl;
import org.onap.dcae.utils.eelf.logger.model.info.MiscLogInfoImpl;
import org.onap.dcae.utils.eelf.logger.model.info.RequestTimingLogInfoImpl;
import org.onap.dcae.utils.eelf.logger.model.info.ResponseLogInfoImpl;
import org.onap.dcae.utils.eelf.logger.model.info.ServiceLogInfoImpl;
import org.onap.dcae.utils.eelf.logger.model.info.TargetServiceLogInfoImpl;
import org.onap.dcae.utils.eelf.logger.model.spec.OptionalLogSpecImpl;

import java.util.Date;

import static org.onap.dcae.utils.eelf.logger.logback.utils.LogUtils.createDefaultAppLogInfo;


/**
 * This utility class various default implementations for EELF Logger. Users should use these default rather then
 * creating their own {@link LogInfo} objects.
 *
 * @author Rajiv Singla
 */
public class EELFLoggerDefaults {

    private static final String UNKNOWN_FIELD_VALUE = "UNKNOWN";

    // =============== APP LOG SPEC ======================//
    /**
     * Provides Default {@link AppLogInfoImpl}
     */
    public static final AppLogInfoImpl DEFAULT_APP_LOG_INFO = createDefaultAppLogInfo();


    // =============== AUDIT LOG SPEC ===================== //

    private static final String DEFAULT_PARTNER_NAME =
            System.getProperty("user.name") != null ? System.getProperty("user.name") : UNKNOWN_FIELD_VALUE;

    public static final ServiceLogInfoImpl DEFAULT_SERVICE_LOG_INFO =
            new ServiceLogInfoImpl(UNKNOWN_FIELD_VALUE, DEFAULT_PARTNER_NAME, "");


    public static final RequestTimingLogInfoImpl DEFAULT_REQUEST_TIMING_LOG_INFO =
            new RequestTimingLogInfoImpl(new Date(), new Date(), null);


    public static final ResponseLogInfoImpl DEFAULT_RESPONSE_LOG_INFO =
            new ResponseLogInfoImpl(900, "UNDEFINED");


    // =============== METRIC LOG SPEC ===================== //

    public static final TargetServiceLogInfoImpl DEFAULT_TARGET_SERVICE_LOG_INFO =
            new TargetServiceLogInfoImpl(UNKNOWN_FIELD_VALUE, UNKNOWN_FIELD_VALUE, UNKNOWN_FIELD_VALUE);

    // =============== ERROR LOG SPEC ===================== //

    public static final ErrorLogInfoImpl DEFAULT_ERROR_LOG_INFO =
            new ErrorLogInfoImpl(900, "UNDEFINED ERROR");


    // ============= OPTIONAL LOG SPEC =================== //

    /**
     * Provides Default {@link CustomFieldsLogInfoImpl}
     */
    public static final CustomFieldsLogInfoImpl DEFAULT_CUSTOM_FIELDS_LOG_INFO =
            new CustomFieldsLogInfoImpl("", "", "", "");

    /**
     * Provides Default {@link MiscLogInfoImpl}
     */
    public static final MiscLogInfoImpl DEFAULT_MISC_LOG_INFO = new MiscLogInfoImpl("", "");


    /**
     * Provides Default {@link OptionalLogSpecImpl}
     */
    public static final OptionalLogSpecImpl DEFAULT_OPTIONAL_LOG_SPEC = new OptionalLogSpecImpl(null, null,
            DEFAULT_CUSTOM_FIELDS_LOG_INFO, DEFAULT_MISC_LOG_INFO);


}
